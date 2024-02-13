import matplotlib.pyplot as plt
import numpy as np
import time

class PlotResults:

    def plot_results(self, data1, data2, label1, label2, filename):

        _, ax = plt.subplots()
        ax.scatter(data1, data2, s=100, c="g", alpha=0.5, cmap=plt.cm.coolwarm, zorder=10)
    
        lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
        ]
    
        ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        plt.xlabel(label1)
        plt.ylabel(label2)
        plt.grid()
        plt.savefig(filename)

class Grid:
    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
      
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
     
        return self._cells

    def get_width(self):
       
        return self._width

    def read_file(self, string_puzzle):
 
        i = 0
        row = []
        for p in string_puzzle:
            if p == '.':
                row.append(self._complete_domain)
            else:
                row.append(p)

            i += 1

            if i % self._width == 0:
                self._cells.append(row)
                row = []
            
    def print(self):
 
        for _ in range(self._width + 4):
            print('-', end=" ")
        print()

        for i in range(self._width):

            print('|', end=" ")

            for j in range(self._width):
                if len(self._cells[i][j]) == 1:
                    print(self._cells[i][j], end=" ")
                elif len(self._cells[i][j]) > 1:
                    print('.', end=" ")
                else:
                    print(';', end=" ")

                if (j + 1) % 3 == 0:
                    print('|', end=" ")
            print()

            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4):
                    print('-', end=" ")
                print()
        print()

    def print_domains(self):
      
        for row in self._cells:
            print(row)

    def is_solved(self):
     
        for i in range(self._width):
            for j in range(self._width):
                if len(self._cells[i][j]) > 1 or not self.is_value_consistent(self._cells[i][j], i, j):
                    return False
        return True
    
    def is_value_consistent(self, value, row, column):
        for i in range(self.get_width()):
            if i == column: continue
            if self.get_cells()[row][i] == value:
                return False
        
        for i in range(self.get_width()):
            if i == row: continue
            if self.get_cells()[i][column] == value:
                return False

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue
                if self.get_cells()[i][j] == value:
                    return False
        return True

class VarSelector:
 
    def select_variable(self, grid):
        pass

class FirstAvailable(VarSelector):
   
    def select_variable(self, grid):
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) > 1:
                    return i, j
 
class MRV(VarSelector):
 
    def select_variable(self, grid):
        minlength = float('inf')
        selected_cell = tuple()

        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if 1 < len(grid.get_cells()[i][j]) < minlength:
                    minlength = len(grid.get_cells()[i][j])
                    selected_cell = (i, j)
        return selected_cell
    
class AC3:
   
    def remove_domain_row(self, grid, row, column):
   
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != column:
                new_domain = grid.get_cells()[row][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[row][j]) > 1:
                    variables_assigned.append((row, j))

                grid.get_cells()[row][j] = new_domain
        
        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
 
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != row:
                new_domain = grid.get_cells()[j][column].replace(grid.get_cells()[row][column], '')
                
                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[j][column]) > 1:
                    variables_assigned.append((j, column))

                grid.get_cells()[j][column] = new_domain

        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
  
        variables_assigned = []

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue

                new_domain = grid.get_cells()[i][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[i][j]) > 1:
                    variables_assigned.append((i, j))

                grid.get_cells()[i][j] = new_domain
        return variables_assigned, False

    def pre_process_consistency(self, grid):
 
        Q = []

        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) == 1:
                    Q.append((i, j))

        return self.consistency(grid, Q)

    def consistency(self, grid, Q):

        while Q:
            var = Q.pop()
            row, column = var

            rows_assigned, row_failure = self.remove_domain_row(grid, row, column)
            columns_assigned, col_failure = self.remove_domain_column(grid, row, column)
            units_assigned, unit_failure = self.remove_domain_unit(grid, row, column)

            if row_failure or col_failure or unit_failure:
                return False  

            for v in rows_assigned + columns_assigned + units_assigned:
                if v not in Q:
                    Q.append(v)

        return True

class Backtracking:
   
    def search(self, grid, var_selector):
        ac3 = AC3()

        if not ac3.pre_process_consistency(grid):
            return None 

        def recursive_search(grid):
            if grid.is_solved():
                return grid

            row, column = var_selector.select_variable(grid)
            for value in grid.get_cells()[row][column]:
                if grid.is_value_consistent(value, row, column):
                    copy_grid = grid.copy()
                    copy_grid.get_cells()[row][column] = value

                    if ac3.consistency(copy_grid, [(row, column)]):
                        result = recursive_search(copy_grid)
                        if result:
                            return result

            return None  

        return recursive_search(grid)


#file = open('tutorial_problem.txt', 'r')
file = open('top95.txt', 'r')
problems = file.readlines()

ac3 = AC3()  
backtracking_solver = Backtracking()

running_time_mrv = []
running_time_first_available = []

for p in problems:
    g = Grid()
    g.read_file(p)

    print('Original Puzzle')
    g.print()

    if ac3.pre_process_consistency(g):
        #print('After Pre-processing with AC3')
        #g.print_domains()

        start_time = time.time()
        var_selector_mrv = MRV()
        solution_mrv = backtracking_solver.search(g, var_selector_mrv)
        end_time = time.time()
        running_time_mrv.append(end_time - start_time)

        g.read_file(p)

        start_time = time.time()
        var_selector_fa = FirstAvailable()
        solution_fa = backtracking_solver.search(g, var_selector_fa)
        end_time = time.time()
        running_time_first_available.append(end_time - start_time)

        var_selector = MRV()

        solution = backtracking_solver.search(g, var_selector)

        if solution:
            print("Solution Found:")
            solution.print()
            g = solution.copy()
        else:
            print("No solution found.")

        print('Is the solved grid a valid solution? ', solution.is_solved() if solution else "N/A")

    else:
        print("No solution found during pre-processing.")
        running_time_mrv.append(None)  
        running_time_first_available.append(None)

plotter = PlotResults()
plotter.plot_results(running_time_mrv, running_time_first_available, "Running Time Backtracking (MRV)", "Running Time Backtracking (FA)", "running_time")