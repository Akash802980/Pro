import axios from "axios";

const MASTER_M3U = "https://raw.githubusercontent.com/Akash802980/nxtm3u/refs/heads/main/Aki.m3u";

export default async function handler(req, res) {
  const { query: { id } } = req;

  try {
    const { data } = await axios.get(MASTER_M3U);
    const regex = new RegExp(
      `#EXTINF[^\\n]*tvg-id="${id}"[\\s\\S]*?(https?://[^\\s]+index\\.mpd[^\\s]*)`,
      "i"
    );
    const match = data.match(regex);

    if (match) {
      res.redirect(match[1]);
    } else {
      res.status(404).send("Not Found");
    }
  } catch (err) {
    res.status(500).send("Server Error: " + err.message);
  }
}
