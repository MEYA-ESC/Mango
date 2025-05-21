.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Avg_R": avg_color[0], "Avg_G": avg_color[1], "Avg_B": avg_color[2],
        "Hue": round(hue,1), "Ripeness": ripeness
    })

# show log
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log")
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode()
    st.download_button("Download log as CSV", csv, "mango_log.csv", "text/csv")
else:
    st.info("Please upload or snap a mango image from the sidebar.")
