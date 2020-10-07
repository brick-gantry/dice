from random import randrange
import re


class GenericDiceParser:
    def parse(self, input: str) -> str:
        total = 0
        rolls = []

        try:
            terms = re.findall("[+-]?[^+-]+", input)
            for term in terms:
                modifier = -1 if term[0] == '-' else 1
                term = re.sub("[+-]", "", term)
                if re.match(r"^\d+$", term):
                    total += modifier * int(term)
                else:
                    parsed = re.match("(\d+)d(\d+)", term)
                    num_dice = int(parsed[1])
                    die_type = int(parsed[2])
                    for _ in range(num_dice):
                        result = randrange(die_type)+1
                        rolls.append(str(result))
                        total += result

            return f"{input} -> ({', '.join(rolls)}) = {total}"
        except:
            return f"Failed to parse: {input}"


class SAGDiceParser:
    def parse(self, input: str) -> str:
        result = 0
        output = []

        try:
            terms = re.findall("[+-]?[^+-]+", input)
            for term in terms:
                modifier = -1 if term[0] == '-' else 1
                term = re.sub("[+-]", "", term)
                if re.match("\d+"):
                    result += modifier * int(term)
                else:
                    parsed = re.match("(\d+)d(\d+)", term)
                    num_dice = int(parsed[1])
                    die_type = int(parsed[2])
                    for _ in range(num_dice):
                        result = randrange(die_type)+1
                        output.append(result)

            return f"({', '.join(output)}) = {result}"
        except:
            raise Exception(f"Failed to parse: {input}")

    def parse(self, input: str):
        try:
            parts = re.findall("[^0-9]*[0-9]*", input)

        except:
            raise Exception(f"Failed to parse: {input}")

    def f(self):
        return [-1, 0, 1][randrange(3)]

    def fa(self):
        return [0, 0, 1][randrange(3)]

    def fd(self):
        return [-1, 0, 0][randrange(3)]
