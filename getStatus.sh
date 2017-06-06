#!/bin/bash
function toFloat {
	echo $(awk "BEGIN {printf \"%.2f\",$(($1 * 2 * 5))/255}")
}

alimentation=$(toFloat $(i2cget -y 1 0x0c))
accumulateur=$(toFloat $(i2cget -y 1 0x0e))
sortie=$(toFloat $(i2cget -y 1 0x0d))

echo ALIMENTATION: $alimentation V
echo ACCUMULATEUR: $accumulateur V
echo SORTIE: $sortie V

