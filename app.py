import streamlit as st

from fact_check import fetch, make_client, verdict

st.set_page_config(page_title="News Fact Checker", page_icon="📰", layout="wide")

st.title("📰 News Fact Checker")
st.caption("Checks how widely a claim is reported by mainstream outlets (coverage, not truth).")


@st.cache_resource
def get_client():
    return make_client()


@st.cache_data(ttl=600, show_spinner=False)
def cached_fetch(claim: str):
    return fetch(get_client(), claim)


with st.form("claim_form", clear_on_submit=False):
    claim = st.text_input(
        "Enter a claim or headline",
        placeholder="e.g. NASA found liquid water on Mars",
    )
    submitted = st.form_submit_button("Check it", type="primary")

if submitted and claim.strip():
    with st.spinner("Searching news and web results…"):
        stories = cached_fetch(claim.strip())

    label, color = verdict(stories)
    banner = {"green": st.success, "yellow": st.warning, "red": st.error}[color]
    banner(f"**{label}** — found {len(stories)} result(s)")

    reputable = [s for s in stories if s.reputable]
    other = [s for s in stories if not s.reputable]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total results", len(stories))
    c2.metric("Reputable outlets", len({s.domain for s in reputable}))
    c3.metric("Other sources", len({s.domain for s in other}))

    if stories:
        st.subheader("Top coverage")
        st.dataframe(
            [
                {
                    "Tier": "🟢 Reputable" if s.reputable else "⚪ Other",
                    "Source": s.source,
                    "Headline": s.title,
                    "Date": s.date,
                    "Link": s.link,
                }
                for s in stories[:20]
            ],
            column_config={"Link": st.column_config.LinkColumn("Link", display_text="Open ↗")},
            hide_index=True,
            use_container_width=True,
        )

        with st.expander("See snippets"):
            for s in stories[:20]:
                tier = "🟢" if s.reputable else "⚪"
                st.markdown(
                    f"{tier} **[{s.title}]({s.link})** — *{s.source}*"
                    + (f"  ·  _{s.date}_" if s.date else "")
                    + f"\n\n{s.snippet or '_(no snippet)_'}"
                )
                st.divider()
    else:
        st.info("No results came back from SerpAPI for that claim.")

elif submitted:
    st.warning("Please enter a claim first.")
