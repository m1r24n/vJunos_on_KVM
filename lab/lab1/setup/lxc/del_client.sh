#!/bin/bash
for i in {1..3}
do
for j in {1..2}
do
lxc stop c${i}${j}
lxc rm c${i}${j}
done
done
