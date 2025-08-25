#!/bin/bash
for i in {1..3}
do
for j in {1..2}
do
lxc stop c${j}site${i}cs2
lxc rm c${j}site${i}cs2
done
done