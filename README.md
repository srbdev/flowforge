# FlowForge

## Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run the following commands:

   ```sh
   git clone https://github.com/srbdev/flowforge.git
   cd flowforge
   uv sync

   # If `~/.local/bin` isn't in your PATH, run:
   # uv tool update-shell
   uv tool install --editable .
   ```
3. Run the CLI tool with the `ff` command

## Usage

```sh
$ ff generate "John has 3 apples, buys 2 bags of 4 apples each, then gives away 5. How many apples does he have?" -o /tmp/graph.json
Graph: apple_count_problem
Description: Calculates the total number of apples John has after buying and giving some away.
Params: initial_apples, bags, apples_per_bag, apples_given_away
Initial params: {'initial_apples': 3.0, 'bags': 2.0, 'apples_per_bag': 4.0, 'apples_given_away': 5.0}

Expression:
  total_bought = multiply(bags, apples_per_bag)
  total_after_buying = add(initial_apples, total_bought)
  total_after_giving = subtract(total_after_buying, apples_given_away)
  output = total_after_giving

Flowchart:
\`\`\`text
flowchart TD
    START --> total_bought
    total_bought[total_bought: multiply(bags, apples_per_bag)]
    total_bought --> total_after_buying
    total_after_buying[total_after_buying: add(initial_apples, total_bought)]
    total_after_buying --> total_after_giving
    total_after_giving[total_after_giving: subtract(total_after_buying, apples_given_away)]
    total_after_giving --> END
\`\`\`
Approve and save? [y/N] y
Saved to /tmp/graph.json

$ ff run /tmp/graph.json
Graph: apple_count_problem
Params: {'initial_apples': 3.0, 'bags': 2.0, 'apples_per_bag': 4.0, 'apples_given_away': 5.0}
Execution:
  total_bought = multiply(bags=2.0, apples_per_bag=4.0) = 8.0
  total_after_buying = add(initial_apples=3.0, total_bought=8.0) = 11.0
  total_after_giving = subtract(total_after_buying=11.0, apples_given_away=5.0) = 6.0
Result: 6.0
```
