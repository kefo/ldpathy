#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

java -jar $DIR/../lib/antlr-4.7.1-complete.jar -Dlanguage=Python3 -o $DIR/../modules/ldprogram/ $DIR/../modules/ldprogram/LDPathProgram.g4

