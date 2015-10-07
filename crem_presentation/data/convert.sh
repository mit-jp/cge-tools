#!/bin/sh

for i in urban_exo cint_n_3 cint_n_4 cint_n_5;
do
  gams pre.gms --file=result_$i
done
