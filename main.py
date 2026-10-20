import streamlit as st
from data import generate_data as gd # game data from ESPN API

# UI Layout
st.set_page_config(page_title="NBA Commentary Generator", layout="wide")

st.title("NBA Commentary Generator 🏀")
st.markdown("You give us a game, we give you the highlights.")



st.header("Game Retrieval")
with st.form("game_selection_form"):

     # Enter league and date and submit to retrieve game data
    league = st.text_input("League", placeholder="e.g. NBA", value="NBA").lower().strip()
    date = st.date_input("Date", help="Select the date of the game you want to retrieve. (Default's to today)")
    readable_date = date.strftime("%Y%m%d")
    submit_button = st.form_submit_button("Get Game Data", use_container_width=True)

if submit_button:
    # Ensure that league and date are provided
    if not league or not date:
        st.error("Please fill in League and Date.")
    else:
        # Thinking spinner while retrieving game data
        with st.spinner(f"Retrieving {league.upper()} game scores for {date}..."):
            search_data = gd.GameData(league=league, date=readable_date)
            search_data.get_games() # Retrieve games for the specified league and date
            if search_data.games:
                st.success(f"Found {len(search_data.games)} {league.upper()} game(s) on {date}.")
                st.subheader("Scoreboard")
                st.caption(f"{date.strftime('%A, %B')} {date.day}, {date.year} · {league.upper()}")

                for game in search_data.games:
                    # Grab highlights for each game and display them in a container
                    highlights = search_data.get_highlights(game["event_id"])
                    with st.container(border=True):
                        st.markdown(f"### {game['game']}")
                        score_col, status_col, summary_col = st.columns([2, 2, 1])
                        score_col.metric("Score", game["gameScore"])
                        status_col.metric("Game status", game["status"])
                        summary_col.link_button(
                            "Game summary",
                            game["link"],
                            use_container_width=True,
                        )

                        with st.expander(f"🎬 Highlights ({len(highlights)})"):
                            if highlights:
                                for highlight in highlights:
                                    st.link_button(
                                        highlight["title"],
                                        highlight["link"],
                                        use_container_width=True,
                                    )
                            else:
                                st.caption("No highlights are available for this game yet.")