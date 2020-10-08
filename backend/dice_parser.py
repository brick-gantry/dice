from random import randrange
import re
from typing import Optional
from backend.dice_exception import DiceException


class GenericDiceParser:
    @staticmethod
    def parse(dice, purpose=None) -> Optional[str]:
        if not dice:
            return None

        total = 0
        rolls = []

        try:
            terms = re.findall("[+-]?[^+-]+", dice)
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
            return f"({dice}) -> ({', '.join(rolls)}) = {total} {purpose or ''}".strip()
        except:
            raise DiceException(f"Failed to parse: \"{dice}\"")


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

    def f(self):
        return [-1, 0, 1][randrange(3)]

    def fa(self):
        return [0, 0, 1][randrange(3)]

    def fd(self):
        return [-1, 0, 0][randrange(3)]
