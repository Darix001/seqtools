# 🧬 seqtools

> **Efficient sequence manipulation for Python**. A powerful toolkit inspired by `itertools` that provides sequence types for more efficient and elegant data handling.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)]()

## ✨ Overview

`seqtools` is a comprehensive Python library that extends the standard `itertools` module with first-class sequence types. Instead of working with iterators, you get fully-featured sequences that support random access, slicing, length queries, and efficient memory usage.

Inspired by the elegance and efficiency of `itertools`, `seqtools` reimagines these tools as proper sequences rather than iterators, giving you the best of both worlds: **lazy evaluation** with **eager access patterns**.

## 🚀 Features

### Core Sequence Types

- **Chaining** - Concatenate multiple sequences with `Chain`
- **Zipping** - Zip sequences together with `Zip` and `ZipLongest`
- **Repetition** - Repeat sequences with `Repeat`, `Mul`, and `Repeats`
- **Combinations** - Generate combinations with `Product`, `Permutations`, and `Nwise`
- **Enumerations** - Enumerate sequences with `Enumerated`
- **Progressions** - Work with `ArithmeticProgression` and `GeometricProgression`

### Key Advantages

✅ **Random Access** - Get any element by index  
✅ **Slicing Support** - Slice sequences like lists  
✅ **Length Queries** - Get sequence length instantly  
✅ **Memory Efficient** - Lazy evaluation under the hood  
✅ **Type Safe** - Built with modern Python type hints  
✅ **Reversible** - Built-in reverse iteration support  

## 📦 Installation

```bash
pip install git+https://github.com/Darix001/seqtools
```

```bash
#with uv (recommended)
uv add git+https://github.com/Darix001/seqtools
```


### Requirements
- Python 3.12+
- attrs >= 26.1.0
- more-itertools >= 11.1.0

## 🎯 Quick Start

### Basic Usage

```python
from seqtools import chain, zip, repeat, mul, progression

# Chain multiple sequences
combined = chain([1, 2, 3], 'asasa', range(5, 6))
print(combined[0])    # 1
print(combined[-1])   # 5
print(combined[5])    # 'a'
print(len(combined))  # 9

# Zip sequences (as a sequence, not an iterator!)
zipped = zip([1, 2, 3], ['a', 'b', 'c'])
print(zipped[0])      # (1, 'a')
print(zipped[2])      # (3, 'c')
print(len(zipped))    # 3

# Repeat values
repeated = repeat('x', 5)
print(repeated[2])    # 'x'
print(len(repeated))  # 5

# Multiply sequences
multiplied = mul(range(3), 4)
print(list(multiplied))   # [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]
print(len(multiplied))    # 12

# Arithmetic progressions
prog = progression(1, 2, 5)  # Start=1, Distance=2, Size=5
print(list(prog))  # [1, 3, 5, 7, 9]
print(prog[2])     # 5
```

### Sequence Views

```python
from seqtools import sview, rview, sslice

# Create a protected view of a sequence
view = sview([1, 2, 3, 4, 5])
print(view[2])     # 3
print(view[1:4])   # Slice(...)

# Create a reverse view without copying
reverse = rview([1, 2, 3, 4, 5])
print(reverse[0])   # 5
print(reverse[-1])  # 1
print(list(reverse))  # [5, 4, 3, 2, 1]
```

### Advanced Operations

```python
from seqtools import nwise, product, enumerated

# N-wise: get sliding windows
pairs = nwise([1, 2, 3, 4, 5], 2)
print(list(pairs))  # [(1, 2), (2, 3), (3, 4), (4, 5)]

# Product: cartesian product as a sequence
prod = product([1, 2], ['a', 'b'], repeat=1)
print(prod[0])   # (1, 'a')
print(len(prod)) # 4

# Enumerated: enumerate as a sequence
enum = enumerated(['a', 'b', 'c'], start=1)
print(enum[0])   # (1, 'a')
print(list(enum)) # [(1, 'a'), (2, 'b'), (3, 'c')]
```

### Utility Functions

```python
from seqtools import get, all_equals, cycle

# Safe get with default
value = get([1, 2, 3], 10, default=None)
print(value)  # None

# Check if all elements are equal
result = all_equals([5, 5, 5, 5])
print(result)  # True

# Cycle through a sequence
cycled = cycle([1, 2, 3], n=2)
print(list(cycled))  # [1, 2, 3, 1, 2, 3]
```

## 📚 API Reference

### Main Sequence Types

#### `Chain(*sequences)`
Concatenates multiple sequences into a single sequence with random access.

```python
x = chain([1, 2], [3, 4], range(5, 7))
print(x[3])    # 4
print(len(x))  # 6
```

#### `Zip(*iterables, strict=False)` / `zip_longest(*iterables, fillvalue=None)`
Zips sequences together like `zip()` but as a proper sequence.

```python
z = zip([1, 2], ['a', 'b'])
print(z[0])  # (1, 'a')
```

#### `Repeat(object, times)`
Repeats a single object `times` times as a sequence.

```python
r = repeat(42, 5)
print(len(r))  # 5
print(r[2])    # 42
```

#### `Mul(sequence, n)`
Multiplies a sequence by repeating it `n` times.

```python
m = mul([1, 2], 3)
print(list(m))  # [1, 2, 1, 2, 1, 2]
print(len(m))   # 6
```

#### `Nwise(sequence, n)`
Creates sliding windows of `n` elements.

```python
nw = nwise([1, 2, 3, 4], 2)
print(list(nw))  # [(1, 2), (2, 3), (3, 4)]
```

#### `Product(*iterables, repeat=1)`
Cartesian product as a sequence.

```python
p = product([1, 2], ['a', 'b'])
print(len(p))  # 4
print(p[0])    # (1, 'a')
```

#### `Enumerated(sequence, start=0)`
Enumerate a sequence while maintaining sequence behavior.

```python
e = enumerated(['x', 'y', 'z'], start=1)
print(e[1])    # (2, 'y')
```

#### `ArithmeticProgression(a1, distance, size)` / `GeometricProgression(a1, ratio, size)`
Mathematical progressions as sequences.

```python
ap = progression(1, 2, 5)  # 1, 3, 5, 7, 9
gp = geometric_progression(1, 2, 5)  # 1, 2, 4, 8, 16
```

### View Types

#### `SequenceView(sequence)` / `sview(sequence)`
Creates a protected view of a sequence without copying data.

#### `ReverseView(sequence)` / `rview(sequence)`
Creates a reverse view of a sequence.

#### `Slice(data, indices)` / `sslice(data, indices)`
Represents a sliced view of a sequence.

### Utility Functions

| Function | Description |
|----------|-------------|
| `get(sequence, index, default=None)` | Safe indexed access with default value |
| `all_equals(sequence)` | Check if all elements are equal |
| `cycle(sequence, n=None)` | Repeat sequence n times (or infinitely) |

## 🏗️ Architecture

### Class Hierarchy

The library is built on a clean inheritance hierarchy:

```
BaseSequence (abstract base)
├── WithData (wraps a sequence)
│   ├── Chain
│   ├── SequenceView / ReverseView
│   └── ...
├── SubSequence (validates items)
│   ├── Zip / ZipLongest
│   ├── Enumerated
│   └── ...
├── Ranged (uses a range object)
│   ├── Repeat
│   ├── ArithmeticProgression
│   └── GeometricProgression
└── Size (generic size wrapper)
    ├── Indexed
    ├── Combinations
    └── ...
```

## 💡 Design Principles

1. **Sequence First** - Everything is a sequence, not an iterator
2. **Random Access** - O(1) or fast lookup for all types where possible
3. **Memory Efficient** - Lazy evaluation with structural sharing
4. **Type Safe** - Full type hints and modern Python patterns
5. **Composable** - Sequence types can be nested and composed

## 🔧 Development

```bash
# Clone the repository
git clone https://github.com/Darix001/seqtools.git
cd seqtools

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
pyright src/seqtools
```

## 📝 Examples

### Working with Data

```python
from seqtools import chain, zip, enumerated, nwise

# Combine multiple data sources
data = chain(
    [(1, 'a'), (2, 'b')],
    [(3, 'c'), (4, 'd')],
    range(5, 7)
)

# Enumerate and create pairs
enhanced = enumerated(nwise(data, 2), start=1)
for idx, (a, b) in enhanced:
    print(f"Pair {idx}: {a} -> {b}")
```

### Efficient Transformations

```python
from seqtools import mul, progression

# Repeat a computation result
results = mul(compute_expensive_operation(), 3)

# Create index ranges
indices = progression(0, 10, size=100)
for i in indices:
    process(data[i])
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

**Dariel Buret** - [@Darix001](https://github.com/Darix001)

## 🙏 Acknowledgments

Inspired by Python's `itertools` module and designed to fill the gap between iterators and sequences.

---

**Made with ❤️ for efficient data manipulation in Python**
