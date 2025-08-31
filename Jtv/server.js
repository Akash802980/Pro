import express from "express";
import fetch from "node-fetch";

const app = express();
const PORT = process.env.PORT || 3000;

// apna master M3U link yaha daalna
const MASTER_M3U = "https://raw.githubusercontent.com/Akash802980/nxtm3u/refs/heads/main/Aki.m3u";

let cache = { data: null, time: 0 };

async function getM3U() {
  const now = Date.now();
  if (cache.data && (now - cache.time < 5 * 60 * 1000)) {
    return cache.data;
  }
  const res = await fetch(MASTER_M3U);
  const text = await res.text();
  cache = { data: text, time: now };
  return text;
}

app.get("/:tvgid", async (req, res) => {
  try {
    const tvgid = req.params.tvgid;
    const m3u = await getM3U();

    // Yeh regex tvg-id ke block ka last line (index.mpd link) extract karega
    const regex = new RegExp(`#EXTINF:[^\\n]*tvg-id="${tvgid}"[\\s\\S]*?(https.*?index\\.mpd[^\\s]*)`, "i");
    const match = m3u.match(regex);

    if (!match) {
      return res.status(404).send("Channel not found in M3U");
    }

    const url = match[1].trim();
    return res.redirect(url);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Error fetching channel");
  }
});

app.listen(PORT, () => {
  console.log(`Proxy running on port ${PORT}`);
});
