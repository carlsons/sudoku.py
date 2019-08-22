#! /usr/bin/zsh

{

   cnt=1
   while ! ./sudoku.py
   do
      printf "\ncnt=%d\n" $((cnt++))
   done
   printf "\ncnt=%d\n" $cnt

} | tee output.txt

