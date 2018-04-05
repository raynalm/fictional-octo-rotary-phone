#!/usr/bin/env lua5.1

local argc = 0
while (arg[argc] ~= nil) do
   argc = argc + 1
end

local num = 3
if (argc == 2) then
   num = tonumber(arg[1])
end

for i=1, num do
   os.execute ("gnome-terminal -e ./.launch_node_fictional-octo-rotary-phone.sh")
end

io.read()

os.execute ("killall .launch_node_fictional-octo-rotary-phone.sh")
