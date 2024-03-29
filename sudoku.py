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



# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# make the game grid

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



   # --------------------------------------------------------------------------------

   # make all the data structures

   choice = None
   choose = xyg_curr

   # identify choices that can't go in the current spot because they have to go
   # in a different spot 
   e_dict         = dict()
   excl_list      = set()

   # create the dictionary that will collect the options for each of the
   # current choices
   c2x_dict       = dict()
   for c in xyg_curr:
      c2x_dict[c] = set()

   # create the dictionary that will collect the options for each of the
   # current choices
   x2c_dict       = dict()

   # create a grid to store the bucketized choices
   c_opts         = mk_grids()
   c_cnt          = 0

   path           = None

   c_exc          = False
   c_bad          = "NO"
   c_lvl          = None


   # --------------------------------------------------------------------------------

   # look at the choices for the current square and decide what do do based on
   # how many there are

   # if the current square has no options, the game is broken; leave
   # choice at None and we'll print an error below
   if not xyg_curr:

      path = 0

   # if the current square has only one option, choose it and skip the the
   # look-ahead
   elif len( xyg_curr ) == 1:

      path = 1
      choice = list( xyg_curr )[0]

   # otherwise, we need to look ahead to constrain the choices we make for this
   # square so we don't break the game
   else:

      path = 2


      # ------------------------------------------------------------------

      # if we're past the first row, but not on the last column, peek ahead and
      # gather data about the options for the remaining squares on this row

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


            # if there's only once choice for this square, then we need
            # to exclude it from the current square

            if len( xyg_peek ) == 1:
               c = list( xyg_peek )[0]
               excl_list.add( c )

            # TODO; at one point, i made this an else if to skip this step if
            # we're adding the item to exlustion list, but that seemed to break
            # the game often enough that we never complete

            if xyg_peek:

               x2c_dict[_x]  = xyg_peek

               # for all of the valid choices, bump the counter in c2x_dict
               for c in xyg_peek:
                  c2x_dict[c].add( _x )


         # TODO: okay, do we have to do this here or can we just subtract the
         # excl_list from the choose options below

         for c in excl_list:
            # get the set of columns where this choice was exclusive
            _c2x = c2x_dict[c]
            # add this to the exclusion list, just for debugging purposes
            e_dict[c] = _c2x
            # but only honor the exclusion if there's only one column
            if len( _c2x ) == 1:
               del c2x_dict[c]


         # now populate the hash buckets based on the number of downstream
         # options each choice has
         for c in c2x_dict.keys():

            # for the current choice, find out how many options are left on the
            # current row
            _cnt = len( c2x_dict[c] )
            # add the choice to the bucket for the given count
            c_opts[ _cnt ].add( c )
            c_cnt += 1



      # ------------------------------------------------------------------



      # check the bucket for those choices having no other options; if there's
      # more than 1 choice, then the game will most likely break
      if len( c_opts[0] ) > 1:

         c_bad = "YES"

      elif len( c_opts[1] ) > 2:

         c_bad = "MAYBE"

      # TODO: it feels like there's a generalization here that we can validate;
      # each bucket can have no more than n+1 items, where n is the index of
      # the bucket (i.e.: the number of downstream options


      # are there *any* downstream options
      if c_cnt:
         for lvl in range( 0, len( c_opts ) ):
            c_opt = c_opts[lvl]
            if len( c_opt ):
               choose = c_opt
               c_lvl  = lvl
               break



      if c_lvl is not None and c_lvl > 0 and len( choose ) > ( c_lvl + 1 ):

         c_exc = True

         # this is experimental code to try to address c_lvl == 1 cases where
         # there are three choices

         x_opts   = list()
         x_choose = set()

         # for each choice in the final set, collect the set of columns for all of
         # them
         for c in choose:
            # if the choice has an entry in the choice to column list
            # TODO: why would a choice not have a list
            if c2x_dict.has_key( c ):
               _c2x = c2x_dict[c]
               if len( _c2x ) == 1:
                  x_opts.append( _c2x )

         # if we have column lists, generate the intersection
         if x_opts:
            x_choose = set.union( *x_opts )



      # make the actual choice

      if choose:
         choice = random.choice( list( choose ) )



   # --------------------------------------------------------------------------------

   # print out the debug spiffle

   if x == 0:
      print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
      last_gx = 0

   if gx != last_gx:
      print "\n----------------------------------------"
      last_gx = gx

   print ""

   print_indicies( idxs )

   print "   ranks      = %s" % pprint.pformat( ranks,          indent=6 )
   print "   xyg_curr   = %s" % pprint.pformat( xyg_curr,       indent=6 )
   print "   path       = %d" % path

   if excl_list:
      print ""
      print "   excl       = %s" % pprint.pformat( excl_list,   indent=6 )
      print "   e_dict     = %s" % pprint.pformat( e_dict,      indent=6 )
      print ""

   print "   c2x        = %s" % pprint.pformat( c2x_dict,       indent=6 )
   print "   x2c        = %s" % pprint.pformat( x2c_dict,       indent=6 )

   print "   c_bad      = %s" % str( c_bad )

   if c_lvl is not None:
      print "   c_lvl      = %d" % c_lvl

   print "   c_opts     = %s" % pprint.pformat( c_opts,         indent=6 )

   if c_exc:
      print ""
      print "   x_opts     = %s" % pprint.pformat( x_opts,      indent=6 )
      print "   x_choose   = %s" % pprint.pformat( x_choose,    indent=6 )
      print ""

   print "   choose     = %s" % pprint.pformat( choose,         indent=6 )

   print ""
   print "   choice     = %s" % choice



   # --------------------------------------------------------------------------------

   # handle the results

   if choice:

      # this add the current choice the result list
      result.append( choice )

      # this updates all current ranks to remove the choice we made
      for r in ranks:
         r.remove( choice )

   else:

      # bark an error
      print "\n\n***** ERROR *****\n"
      # and break the main loop that's iterating all the squares
      break



# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print out the results

print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"

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

