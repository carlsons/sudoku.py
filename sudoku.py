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

   return ( i, x, y, gi, gx, gy, gsx, gsy )


def get_indicies_xy( x, y ):

   i     = ( y * 9 ) + x

   gx    = x / 3
   gy    = y / 3
   gi    = ( gy * 3 ) + gx

   gsx   = x - ( gx * 3 )
   gsy   = y - ( gy * 3 )

   return ( i, x, y, gi, gx, gy, gsx, gsy )


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

   # this union describes all of the choices for the current spot
   xyg_curr         = set.intersection( x_rank, y_rank, g_rank )



   # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


   # identify choices that can't go in the current spot because they have to go
   # in a different spot 
   e_dict    = dict()
   excl_list = set()



   # create the dictionary that will collect the options for each of the
   # current choices
   c2x_dict = dict()
   for c in xyg_curr:
      c2x_dict[c] = set()

   # create the dictionary that will collect the options for each of the
   # current choices
   x2c_dict = dict()


   # create a grid to store the bucketized choices
   c_opts = mk_grids()
   c_cnt  = 0

   # if we're past the first row, but not on the last column
   if y > 0 and x < 8:


      # peek ahead and gather statistics about the remaining choices

      for _x in range( x+1, 9 ):



         # get the indicies of the given spot
         _idxs = get_indicies_xy( _x, y )
         _i, _x, _y, _gi, _gx, _gy, _gsx, _gsy = _idxs

         # get the column and grid ranks for the given spot
         _x_temp  = x_ranks[ _x ]
         _g_temp  = g_ranks[ _gi ]

         # and take the instersection to see if any of the choice for the
         # current spot are valid choiices for the given spot
         xyg_peek   = set.intersection( xyg_curr, _x_temp, _g_temp )


         if len( xyg_peek ) == 1:
            c = list( xyg_peek )[0]
            excl_list.add( c )


         if xyg_peek:

            x2c_dict[_x]  = xyg_peek

            # for all of the valid choices, bump the counter in c2x_dict
            for c in xyg_peek:
               c2x_dict[c].add( _x )



      for c in excl_list:
         e_dict[c] = c2x_dict[c]
         del c2x_dict[c]


      # now populate the bucketized choices
      for c in c2x_dict.keys():

         # for the current choice, find out how many options are left on the
         # current row
         _cnt = len( c2x_dict[c] )
         # add the choice to the bucket for the given count
         c_opts[ _cnt ].add( c )
         c_cnt += 1





   choose = set()
   choice = None


   # make sure the zero bucket is less than 2; this bucket contains those
   # choices that have no other possible spots on this line if we have
   # more than 1, then we can't complete this game grid
   if len( c_opts[0] ) < 2:

      if c_cnt:
         for c_opt in c_opts:
            if len( c_opt ):
               choose = c_opt
               break

      if not choose:
         choose = xyg_curr



   x_opts   = list()
   x_choose = set()

   # for each choice in the final set, collect the set of columns for all of
   # them
   for c in choose:
      # if the choice has an entry in the choice to column list
      # TODO: why would a choice not have a list
      if c2x_dict.has_key( c ):
         x_opts.append( c2x_dict[c] )

   # if we have column lists, generate the intersection
   if x_opts:
      x_choose = set.intersection( *x_opts )



   if choose:
      choice = random.choice( list( choose ) )


   # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-



   if x == 0:
      print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
      last_gx = 0

   if gx != last_gx:
      print "\n----------------------------------------"
      last_gx = gx

   print ""

   print_indicies( idxs )

   print "   ranks      = %s" % pprint.pformat( ranks,       indent=6 )
   print "   xyg_curr   = %s" % pprint.pformat( xyg_curr,      indent=6 )

   if excl_list:
      print ""
      print "   excl       = %s" % pprint.pformat( excl_list,   indent=6 )
      print "   e_dict     = %s" % pprint.pformat( e_dict,      indent=6 )
      print ""

   print "   c2x        = %s" % pprint.pformat( c2x_dict,    indent=6 )
   print "   x2c        = %s" % pprint.pformat( x2c_dict,    indent=6 )
   print "   c_opts     = %s" % pprint.pformat( c_opts,      indent=6 )
   print "   x_opts     = %s" % pprint.pformat( x_opts,      indent=6 )
   print "   x_ch       = %s" % pprint.pformat( x_choose,    indent=6 )
   print "   choose     = %s" % pprint.pformat( choose,      indent=6 )

   if choice:
      result.append( choice )
      for r in ranks:
         r.remove( choice )

   print "   ranks  = %s" % pprint.pformat( ranks, indent=6 )
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




