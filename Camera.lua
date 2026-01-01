local HttpService = game:GetService("HttpService")

local URL = "https://camera-voxel-roblox.onrender.com/cameraGet"

local GRID = 64
local PIXEL = 8
local DEPTH = 15

local part = Instance.new("Part")
part.Anchored = true
part.Size = Vector3.new(64, 64, 1)
part.Position = Vector3.new(0, 32, 0)
part.Parent = workspace

local gui = Instance.new("SurfaceGui")
gui.Face = Enum.NormalId.Front
gui.AlwaysOnTop = true
gui.CanvasSize = Vector2.new(GRID * PIXEL, GRID * PIXEL)
gui.Parent = part

local frames = {}
local index = 1

for row = 0, GRID - 1 do
	for col = 0, GRID - 1 do
		local f = Instance.new("Frame")
		f.Size = UDim2.fromOffset(PIXEL, PIXEL)
		f.Position = UDim2.fromOffset(col * PIXEL, row * PIXEL)
		f.BorderSizePixel = 0
		f.BackgroundColor3 = Color3.new(0,0,0)
		f.Parent = gui

		frames[index] = f
		index += 1
	end
end

while true do
	local ok, res = pcall(function()
		return HttpService:GetAsync(URL, true)
	end)

	if ok then
		local data = HttpService:JSONDecode(res)

		if data.ready then
			for i, rgb in ipairs(data.data) do
				local f = frames[i]
				if f then
					f.BackgroundColor3 = Color3.fromRGB(
						rgb[1],
						rgb[2],
						rgb[3]
					)
				end
			end
		end
	end

	task.wait(0.3)
end
