-- One-shot run: screenshots at fixed frames, then a DONE marker for the wrapper to kill mGBA
-- (emu:quit() is not reliable). Output dir = $PLAYTEST_OUT or the current directory.
local out = (os.getenv("PLAYTEST_OUT") or ".") .. "/"
local shots = {[300]=true, [900]=true, [1800]=true}
callbacks:add("frame", function()
  local f = emu:currentFrame()
  if shots[f] then emu:screenshot(out .. "frame_" .. f .. ".png"); console:log("shot " .. f) end
  if f == 1801 then local h = io.open(out .. "DONE", "w"); h:write("ok"); h:close() end
end)
