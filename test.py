import unittest
from main import (
    read_input, validate_colour, validate_solution,
    MRV, LCV, AC3, search, remove
)

class TestValidateColour(unittest.TestCase):

    def setUp(self):
        # Simple triangle graph (K3) used across all tests in this class
        self.adj = {'1': {'2', '3'}, '2': {'1', '3'}, '3': {'1', '2'}}

    def test_valid_colour(self):
        # Vertex 1 should be assignable to colour 3 since
        # neighbour 2 has colour 1 and neighbour 3 has colour 2 - no conflict
        coloured = {'2': 1, '3': 2}
        self.assertTrue(validate_colour('1', 3, coloured, self.adj))

    def test_invalid_colour(self):
        # Vertex 1 should NOT be assignable to colour 1 since
        # neighbour 2 already has colour 1 - conflict
        coloured = {'2': 1, '3': 2}
        self.assertFalse(validate_colour('1', 1, coloured, self.adj))

    def test_no_neighbours_coloured(self):
        # Any colour should be valid if no neighbours have been coloured yet
        self.assertTrue(validate_colour('1', 1, {}, self.adj))


class TestAC3(unittest.TestCase):

    def setUp(self):
        # Simple triangle graph (K3) used across all tests in this class
        self.adj = {'1': {'2', '3'}, '2': {'1', '3'}, '3': {'1', '2'}}

    def test_ac3_reduces_domain(self):
        # Vertex 1 is pre-assigned to colour 1 (singleton domain)
        # AC3 should propagate and remove colour 1 from neighbours 2 and 3
        domain = {'1': {1}, '2': {1, 2, 3}, '3': {1, 2, 3}}
        AC3(domain, self.adj)
        self.assertNotIn(1, domain['2'])
        self.assertNotIn(1, domain['3'])

    def test_ac3_detects_no_solution(self):
        # Vertices 1 and 2 are both forced to colour 1 but they are adjacent
        # AC3 should detect this conflict and return False
        domain = {'1': {1}, '2': {1}, '3': {1, 2, 3}}
        result = AC3(domain, self.adj)
        self.assertFalse(result)

    def test_ac3_full_domains_unchanged(self):
        # When all domains are full, AC3 has nothing to propagate
        # so no domain sizes should change
        domain = {'1': {1, 2, 3}, '2': {1, 2, 3}, '3': {1, 2, 3}}
        before = {v: len(domain[v]) for v in domain}
        AC3(domain, self.adj)
        after = {v: len(domain[v]) for v in domain}
        self.assertEqual(before, after)


class TestRemove(unittest.TestCase):

    def test_removes_when_y_singleton(self):
        # Y has only colour 1, so colour 1 should be removed from X's domain
        # since X and Y are constrained to be different
        domain = {'1': {1, 2, 3}, '2': {1}}
        removed = remove(domain, '1', '2')
        self.assertTrue(removed)
        self.assertNotIn(1, domain['1'])

    def test_no_remove_when_y_not_singleton(self):
        # Y has colours 1 and 2, so no colour in X is fully blocked
        # remove should return False and leave X's domain unchanged
        domain = {'1': {1, 2, 3}, '2': {1, 2}}
        removed = remove(domain, '1', '2')
        self.assertFalse(removed)


class TestSearch(unittest.TestCase):

    def setUp(self):
        # Simple triangle graph (K3) used across all tests in this class
        self.adj = {'1': {'2', '3'}, '2': {'1', '3'}, '3': {'1', '2'}}
        self.vertices = {'1', '2', '3'}

    def test_finds_solution(self):
        # A triangle with 3 colours is solvable - search should return a result
        domain = {v: {1, 2, 3} for v in self.vertices}
        result = search(self.vertices, self.adj, {}, 3, domain)
        self.assertIsNotNone(result)

    def test_no_solution(self):
        # A triangle requires at least 3 colours - with only 2 available
        # search should return None indicating no solution exists
        domain = {v: {1, 2} for v in self.vertices}
        result = search(self.vertices, self.adj, {}, 2, domain)
        self.assertIsNone(result)

    def test_solution_is_valid(self):
        # The solution returned by search should pass the validate_solution check
        # meaning no adjacent vertices share a colour and all colours are in range
        domain = {v: {1, 2, 3} for v in self.vertices}
        result = search(self.vertices, self.adj, {}, 3, domain)
        self.assertTrue(validate_solution(result, self.adj, 3, self.vertices))


class TestValidateSolution(unittest.TestCase):

    def setUp(self):
        # Simple triangle graph (K3) used across all tests in this class
        self.adj = {'1': {'2', '3'}, '2': {'1', '3'}, '3': {'1', '2'}}
        self.vertices = {'1', '2', '3'}

    def test_valid_solution(self):
        # All vertices have different colours and no adjacent pair shares a colour
        # this is a correct 3-colouring of the triangle
        result = {'1': 1, '2': 2, '3': 3}
        self.assertTrue(validate_solution(result, self.adj, 3, self.vertices))

    def test_invalid_adjacent_same_colour(self):
        # Vertices 1 and 2 are adjacent and both have colour 1
        # this violates the colouring constraint
        result = {'1': 1, '2': 1, '3': 3}
        self.assertFalse(validate_solution(result, self.adj, 3, self.vertices))

    def test_invalid_colour_out_of_range(self):
        # Vertex 3 has colour 5 but only 3 colours are allowed
        # this should be rejected as invalid
        result = {'1': 1, '2': 2, '3': 5}
        self.assertFalse(validate_solution(result, self.adj, 3, self.vertices))

    def test_missing_vertex(self):
        # Vertex 3 has not been assigned a colour
        # an incomplete solution should be rejected
        result = {'1': 1, '2': 2}
        self.assertFalse(validate_solution(result, self.adj, 3, self.vertices))


if __name__ == "__main__":
    unittest.main()