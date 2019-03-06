from collections import deque, defaultdict

import sys

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


class AhoCorasick(object):
    def __init__(self, dictionary, values):
        self.build_trie(dictionary, values)
        self.build_fails()

    def build_trie(self, dictionary, values):
        self.trie = trie = [{}]
        self.outputs = outputs = defaultdict(dict)  # state => index => value
        state = 0
        for index, word in enumerate(dictionary):
            state = 0
            for char in word:
                if char not in trie[state]:
                    new = len(trie)
                    trie[state][char] = new
                    trie.append({})
                state = trie[state][char]
            outputs[state][index] = values[index]  # Avoid checking for state with defaultdict
    
    def build_fails(self):
        # Avoid . lookups
        trie = self.trie
        suffixes = self.suffixes
        outputs = self.outputs
        
        self.fails = fails = { state: 0 for state in trie[0].values() }
        self.memoize_output = memoize_output = defaultdict(list)
        
        # states = [(parent, char, state)]
        states = deque([(0, c, s) for c, s in trie[0].items()])  # BFS
        pop_state = states.popleft
        push_state = states.append
        while states:
            parent, char, state = pop_state()
            suffix_found = False
            for parent_suffix in suffixes(parent):
                # Follow fails until one has a child with same letter
                try:  # This is called many, many times. .get() is too slow
                    suffix = trie[parent_suffix][char]
                except KeyError:
                    continue
                if not suffix_found:
                    fails[state] = suffix
                    suffix_found = True
                if suffix in outputs:
                    memoize_output[state].append(suffix)  # Avoid checking for state with defaultdict
            if state not in fails:
                fails[state] = 0  # Default to fail to root
            for char, next_state in trie[state].items():
                push_state((state, char, next_state))
    
    def suffixes(self, state):
        fails = self.fails  # Local variable for performance
        try:  # .get() too slow
            suffix = fails[state]
        except KeyError:
            return
        while True:
            yield suffix
            try:
                suffix = fails[suffix]
            except KeyError:
                return
    
    def goto(self, state, letter):
        # try child
        next_state = self.trie[state].get(letter)
        if next_state:
            return next_state
        # try suffix children
        for suffix in self.suffixes(state):
            next_state = self.trie[suffix].get(letter)
            if next_state:
                return next_state
        return 0  # if all fails return root
    
    def values(self, state, low_index, high_index):
        outputs = [state] if state in self.outputs else []
        if state in self.memoize_output:
            outputs.extend(self.memoize_output[state])
        for output in outputs:
            for index, value in self.outputs[output].items():
                if low_index <= index <= high_index:
                    yield value

    def value(self, string, low_index, high_index):
        state = 0
        val = 0
        for c in string:
            state = self.goto(state, c)
            val += sum([v for v in self.values(state, low_index, high_index)])
        return val

def main():
    with open('fail.txt') as inputs:
        n = int(inputs.readline())
        genes = inputs.readline().rstrip().split()
        health = list(map(int, inputs.readline().rstrip().split()))
        s = int(inputs.readline())

        least = float('inf')
        most = float('-inf')
        
        aho = AhoCorasick(genes, health)

        for s_itr in range(s):
            firstLastd = inputs.readline().split()

            first = int(firstLastd[0])
            last = int(firstLastd[1])
            dna = firstLastd[2]

            score = aho.value(dna, first, last)

            if score < least:
                least = score
            if score > most:
                most = score
        
        print(least, most)


if __name__ == '__main__':
    main()