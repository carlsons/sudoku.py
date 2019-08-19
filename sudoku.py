#! /usr/bin/python

import sys
import random
import pprint

DEBUG = False


# define the generator functions


def mk_master_idx():
   return  range( 0, 81 )


def mk_rank():
   return set( range( 1, 10 ) )


def mk_ranks():
   r = list()
   for x in mk_rank():
      r.append( mk_rank() )
   return r


def mk_game_data():
   return [ mk_ranks(), mk_ranks(), mk_ranks() ]


def mk_grids():
   g = list()
   for x in mk_rank():
      g.append( set() )
   return g


def get_indicies( i ):

   x     = i % 9
   y     = i / 9

   gx    = x / 3
   gy    = y / 3
   gi    = ( gy * 3 ) + gx

   gsx   = x - ( gx * 3 )
   gsy   = y - ( gy * 3 )

   return ( idx, x, y, gi, gx, gy, gsx, gsy )

def print_indicies( idx ):
   print "%2d: x=%d, y=%d, gi=%d, gx=%d, gy=%d, gsx=%d, gsy=%d" % idxs


# set up the game meta data

# this is the raw data, used to constrain the choice for each spot
game_data = mk_game_data()
x_ranks, y_ranks, g_ranks = game_data

# this is where we store answers for each grid so we can further constrain
# choises
grids = mk_grids()
cols  = mk_grids()

# pprint.pprint( game_data )

master_idx  = mk_master_idx()
shuffle_idx = random.shuffle( mk_master_idx() )

if DEBUG:

   print "\ndump indicies\n"

   for idx in master_idx:
      idxs = get_indicies( idx )
      print_indicies( idxs )

print "\nmake game"

last_gx = 0

result = list()

for idx in master_idx:

   idxs = get_indicies( idx )
   i, x, y, gi, gx, gy, gsx, gsy = idxs

   # get the ranks for the current column, row and grid
   x_rank         = x_ranks[ x ]    # columns
   y_rank         = y_ranks[ y ]    # rows
   g_rank         = g_ranks[ gi ]   # grids
   # toss them into a list so we can handle the updates below
   ranks          = [ x_rank, y_rank, g_rank ]

   # get the current sets of choices
   grid           = grids[ gi ]
   col            = cols[ x ]

   # this union describes all of the choices for the current spot
   u_spot         = set.intersection( x_rank, y_rank, g_rank )



   g_next = set()
   if y > 0 and x < 8:
      for _x in range( x+1, 9 ):
         g_next   = set.union( g_next, cols[_x] )

   if g_next:
      choose      = set.intersection( u_spot, g_next )
   else:
      choose      = u_spot

   # now make a choice
   choice = None
   if choose:
      choice = random.choice( list( choose ) )
   elif u_spot:
      choice = random.choice( list( u_spot ) )



   if x == 0:
      print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
      last_gx = 0

   if gx != last_gx:
      print "\n----------------------------------------"
      last_gx = gx

   print ""

   print_indicies( idxs )

   print "   ranks  = %s" % pprint.pformat( ranks,  indent=6 )
   print "   u_spot = %s" % pprint.pformat( u_spot, indent=6 )
   print "   g_next = %s" % pprint.pformat( g_next, indent=6 )
   print "   choose = %s" % pprint.pformat( choose, indent=6 )

   if choice:
      result.append( choice )
      for r in ranks:
         r.remove( choice )
      grid.add( choice )
      col.add( choice )

   print "   ranks  = %s" % pprint.pformat( ranks, indent=6 )
   print "   grid   = %s" % pprint.pformat( grid, indent=6 )
   print ""
   print "   choice = %s" % choice


   if not choice:
      print "\n\n***** ERROR *****\n"
      break


last_gx = 0
last_gy = 0

for idx in range( 0, len(result) ):

   idxs = get_indicies( idx )
   i, x, y, gi, gx, gy, gsx, gsy = idxs

   if x == 0:
      print ""
      print "",
      last_gx  = 0

   if gx != last_gx:
      last_gx = gx
      print "|",

   if gy != last_gy:
      last_gy = gy
      print "----------------------"
      print "",

   print "%d" % result[ idx ],


if len(result) == 81:
   print "\n\n***** SUCCESS *****\n"
   sys.exit(0)

sys.exit(1)




