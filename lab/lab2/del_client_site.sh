#!/bin/bash
for i in {1..3}
do
for j in {1..3}
do
lxc stop c${j}site${i}
lxc rm c${j}site${i}
done
done