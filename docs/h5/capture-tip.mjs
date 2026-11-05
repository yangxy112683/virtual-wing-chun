const DEBUG_AUDIENCE = /^(unknown|straight|bridge)(\s|$)|^检出 |弱特征|方向不明|上下接近|未出招|无人|出画|dy=/;

export function captureTipAudience(text) {
  if (!text) return "player";
  return DEBUG_AUDIENCE.test(text) ? "debug" : "player";
}

export function showCaptureTipText(text, debugOn) {
  if (!text) return "";
  if (captureTipAudience(text) === "debug" && !debugOn) return "";
  return text;
}

export function composeCaptureTip(playerText, debugText, debugOn) {
  const player = playerText || "";
  if (!debugOn || !debugText || captureTipAudience(debugText) !== "debug") return player;
  if (!player) return debugText;
  return player + " · " + debugText;
}

export function releaseDebugCaptureTip(text) {
  if (!text) return "";
  const parts = text.split(" · ");
  while (parts.length > 1 && captureTipAudience(parts[parts.length - 1]) === "debug") {
    parts.pop();
  }
  const joined = parts.join(" · ");
  if (captureTipAudience(joined) === "debug") return "";
  return joined;
}
