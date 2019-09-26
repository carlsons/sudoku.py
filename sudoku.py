#! /usr/bin/python



# terminology
#  grid     - 9x9 game board consisting of 81 cells
#  rows     - horizontal grouping of 9 cells
#  columns  - vertical grouping of 9 cells
#  boxes    - 3x3 grouping of 9 cells
#  band     - row of boxes
#  stack    - column of boxes
#  cell     - one of 81 positions in a sudoku grid, contains one choice

#  clues    - a.ka. "givens", known values at the start of a game


import sys
import random
import pprint

DEBUG = False




# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


class SudokuLookahead:

   def __init__( self, grid, cell ):

      self.grid            = grid                        # the grid
      self.cell            = cell                        # the cell we're tyring to choose


   def scan( self, idxs, get_cell ):

      i2c_dict             = dict()                      # maps the index to the choices available

      c2i_dict             = dict()                      # maps the choice to the available cells
      for c in self.cell.choices:
         c2i_dict[c]       = set()

      excl_list            = set()                       # set of choices that have to go in a another spot
      excl_dict            = dict()                      # maps excluded choices to their available cells

      buckets              = self.grid.mk_empty_sets()   # used to bucketize choices based on the number of options
      bucket_cnt           = 0


      # step 1: scan the indexs, get the available options and update the cross
      # references

      for i in idxs:

         # get the cell for the given index
         cell = get_cell( i )
         # take the intersection of the two cell to see if any of the choice
         # for the base cell are valid for the one we're looking at
         peek = set.intersection( self.cell.choices, cell.choices )

         if peek:

            if len( peek ) == 1:
               c = list( peek )[0]
               excl_list.add( c )

            # save the choices for this index
            i2c_dict[i]    = peek

            # and add this index to the bucket for each of the available choices
            for c in peek:
               c2i_dict[c] = i

      # step 2: pull things out of the cross reference that we can use

      for c in excl_list:
         # get the set of columns where this choice was exclusive
         c2i               = c2i_dict[c]
         # add this to the exclusion list, just for debugging purposes
         excl_dict[c]      = c2i
         # but only honor the exclusion if there's only one possible cell
         if len( c2i ) == 1:
            del c2i_dict[c]

      # step 3: now populate the hash buckets based on the number of downstream
      # options each choice has

      for c in c2i_dict.keys():

         # for the current choice, find out how many options are left
         cnt = len( c2i_dict[c] )
         # add the choice to the bucket for the given count
         buckets[ cnt ].add( c )
         bucket_cnt += 1







# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class SudokuCell:

   def __init__( self, grid, cell_idx ):

      self.grid            = grid                        # the grid that owns this cell
      self.cell_idx        = cell_idx                    # the cell index 0..80 within the grid

      self.idxs            = self.grid.get_indicies( cell_idx )    # all of the relevant index values for the given cell

      # split the index values into individual fields
      #
      #  i     same as cell_idx  0..80 cell           index,               left to right, top to bottom
      #  x     column index      0..8  cell column    index within grid,   left to right
      #  y     row index         0..8  cell row       index within grid,   top to bottom
      #  bi    box index         0..8  box index      within grid,         left to right, top to bottom
      #  bx    stack index       0..3  stack index    within grid,         left to right
      #  by    band index        0..3  band index     within grid,         top to bottom
      #  bsi   box cell index    0..9  cell index     within box,          left to right, top to bottom
      #  bsx   box col  index    0..3  cell column    within box,          left to right
      #  bsy   box row  index    0..3  cell row       within box,          top to bottom

      self.i,     \
      self.x,     \
      self.y,     \
      self.bi,    \
      self.bx,    \
      self.by,    \
      self.bsi    \
      self.bsx,   \
      self.bsy    \
                           = idxs

      # get the remaining choices for the column, row and box
      self.col             = self.grid.get_col( self.x )    # available choices for the current column
      self.row             = self.grid.get_row( self.y )    # available choices for the current row
      self.box             = self.grid.get_box( self.bi )   # available choices for the current box

      # stow them into a list so we can update once we've made a choice for
      # this cell
      self.choice_sets     = [ self.col, self.row, self.box ]

      # the intersection of remaining choices for the column row and box yields
      # the choices that are valid for the current cell
      self.choices         = set.intersection( x_rank, y_rank, g_rank )
      self.choices_len     = len( choices )

      # this is the choice made for this cell and a descriptor to identify how
      # it was chosen
      self.choice          = None


   def get_choice( self ):
      return self.choice





   def get_cell_by_x( self, x ):

      i = self.grid.get_index( x, self.y )
      return SudokuCell( self.grid, i )







   def choose( self ):

      if not self.choices_len:

         # if the current cell has no options, the game is broken
         pass

      elif self.choices_len == 1:


         # if the current cell has only one option, choose it and skip the the
         # look-ahead
         self.choice       = list( self.choices )[0]

      else:

         if self.y > 0 and self.x < 8:

















# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class SudokuGrid:

   def __init__( self ):

      # set up the game meta data

      # this is the raw data, i.e.: the sets that to constrain the choices for
      # each cell
      self.game_data                   = Sudoku.mk_game_data()
      self.cols, self.rows, self.boxes = self.game_data

      self.cells                       = dict()


   def get_col( self, x ):
      return self.cols[x]


   def get_row( self, y ):
      return self.rows[y]


   def get_box( self, bi ):
      return self.boxes[bi]


   def print_grid( self ):

      bar = "-" * 22
      last_bx = 0
      last_by = 0

      for idx in self.cell_idxs:

         idxs = self.get_indicies( idx )
         i, x, y, bi, bx, by, bsi, bsx, bsy = idxs

         ch = "?"
         if self.cells.has_key( idx ):
            ch_num = self.cells[ idx ].get_choice()
            ch = str( ch_num )

         if x == 0:
            print ""
            print "",
            last_bx = 0

         if bx != last_bx:
            last_bx = bx
            print "|",

         if by != last_by:
            last_by = by
            print bar
            print "",

         print "%s" % ch,

      print ""
      print bar






   def generate( self ):

      for cell_idx in self.cell_idxs:

         cell = SudokuCell( self, idx )

















   # ------------------------------------------------------------

   base_idxs   = range( 0, 9 )
   cell_idxs   = range( 0, 81 )

   # static methoods

   @staticmethod
   def mk_set():
      return set( range( 1, 10 ) )


   @staticmethod
   def mk_sets():
      r = list()
      for x in SudokuGrid.base_idxs:
         r.append( SudokuGrid.mk_set() )
      return r


   def mk_empty_sets():
      r = list()
      for x in SudokuGrid.base_idxs:
         r.append( set() )
      return r


   @staticmethod
   def mk_game_data():
      return [ Sudoku.mk_sets() for i in range( 0, 3 ) ]


   @staticmethod
   def mk_cell_idxs():
      return range( 0, 81 )


   @staticmethod
   def get_indicies( i ):

      x     = i % 9
      y     = i / 9

      bx    = x / 3
      by    = y / 3
      bi    = ( by * 3 ) + bx

      bsx   = x - ( bx * 3 )
      bsy   = y - ( by * 3 )
      bsi   = ( y * 3 ) + x

      return ( i, x, y, bi, bx, by, bsi, bsx, bsy )


   @staticmethod
   def get_index( x, y ):

      return ( y * 9 ) + x


   @staticmethod
   def get_indicies_xy( x, y ):

      i     = ( y * 9 ) + x

      return SudokuGrid.get_indicies( i )


   @staticmethod
   def print_indicies( idx ):
      print "%2d: x=%d, y=%d, bi=%d, bx=%d, by=%d, bsi=%d, bsx=%d, bsy=%d" % idxs




















# define the generator functions








# pprint.pprint( game_data )


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
   c_opts         = mk_empty_sets()
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


if len(result) == 81:
   print "\n\n***** SUCCESS *****\n"
   sys.exit(0)

sys.exit(1)

