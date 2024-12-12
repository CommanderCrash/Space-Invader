<h1 align="center">Space Invader</h1>

<p align="center">
  A Python script to send codes via a 433/315MHz GPIO device on a Raspberry Pi.
</p>

---

## Table of Contents

- <a href="#about">About</a>
- <a href="#features">Features</a>
- <a href="#installation">Installation</a>
- <a href="#usage">Usage</a>
  - <a href="#command-line-options">Command-Line Options</a>
  - <a href="#examples">Examples</a>
- <a href="#license">License</a>

---

<h2 id="about">About</h2>

<p>This script transmits codes through a 433/315MHz GPIO device using various protocols. It provides options for sending specific codes, iterating through brute force modes, and adjusting pulse lengths. The script leverages <code>pigpio</code> for GPIO control and <code>termcolor</code> for colored output in the terminal.</p>

<h2 id="features">Features</h2>

<ul>
  <li>Supports multiple protocols for transmitting codes.</li>
  <li>Options for brute force modes with different code generation strategies.</li>
  <li>Customizable pulse length, protocol, code length, and more.</li>
  <li>Command-line interface for flexible usage and automation.</li>
</ul>

<h2 id="installation">Installation</h2>

<p>Before using this script, ensure the following Python packages are installed:</p>


pip install pigpio termcolor

<p>Additionally, make sure <code>pigpiod</code> (the PiGPIO daemon) is running:</p>



sudo pigpiod

<h2 id="usage">Usage</h2> <p>Run the script with various options to control its behavior. Use the following command to see all available options:</p>



python3 transmitter.py -h

<h3 id="command-line-options">Command-Line Options</h3> <table> <tr> <th>Option</th> <th>Description</th> </tr> <tr> <td><code>-s BASE_CODE</code></td> <td>Base code to start guessing from in brute force mode 3</td> </tr> <tr> <td><code>-g GPIO</code></td> <td>GPIO pin to use (Default: 17)</td> </tr> <tr> <td><code>-p PULSELENGTH</code></td> <td>Pulselength (Default: None, uses protocol's default)</td> </tr> <tr> <td><code>-t PROTOCOL</code></td> <td>Protocol(s) to use. Use <code>-t all</code> to iterate through all protocols.</td> </tr> <tr> <td><code>-l LENGTH</code></td> <td>Code length (Default: 24)</td> </tr> <tr> <td><code>-r REPEAT</code></td> <td>Repeat cycles (Default: 10)</td> </tr> <tr> <td><code>-bf MODE</code></td> <td>Brute force mode (1: Count up, 2: Random, 3: Guess based on '?')</td> </tr> <tr> <td><code>-m BINARY_STRING</code></td> <td>Send a single code in binary string format. Not compatible with <code>-bf</code> or <code>-l</code></td> </tr> <tr> <td><code>-to TIMEOUT</code></td> <td>Timeout in milliseconds between protocols when using <code>-t all</code> (Default: 0)</td> </tr> </table> <h3 id="examples">Examples</h3> <p>1. Sending a single code using protocol 1 on GPIO 17:</p>

```bash

python3 transmitter.py -m 101010 -g 17 -p 350 -t 1

<p>2. Brute force mode 1 with 24-bit code length:</p>

```

python3 transmitter.py -bf 1 -l 24 -t 1
```
<p>3. Sending a code using custom pulse and space lengths:</p>


python3 transmitter.py -m 111000 -g 17 --sync_pulse 32 --sync_space 50 --zero_pulse 1 --zero_space 3 --one_pulse 3 --one_space 1

<h2 id="license">License</h2> <p>This project is open source and available under the MIT License.</p> ```

This template provides a well-structured layout for your script's README.md, focusing on usage examples and command-line options, which should help users get started quickly.
