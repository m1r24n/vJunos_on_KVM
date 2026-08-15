#!/usr/bin/env bash
for i in wan1 wan2 lan1a lan1b lan2
do
	sudo ip link add dev $i type bridge
	sudo ip link set dev $i up

done
