# -*- Encoding: windows-1251 -*-

class Parser:
    def __init__(self):
        self.query = ""
        self.token = ""
        self.minus = False
        self.minusBracket = 0
        self.quote = False

    def nextToken(self):
        if len(self.query) > 0:
            self.token = self.query[0]
            self.query = self.query[1:]
        else:
            self.token = None

    def s0(self):
        x = self.s1()
        if self.token == "|":
            self.nextToken()
            x += self.s0()
        return x

    def s1(self):
        x = []
        if self.token != None:
            if self.token == "(" or (self.token in "\"'" and not self.quote):
                if self.token in "\"'":
                    self.quote = True
                if self.minus or self.minusBracket > 0:
                    self.minus = False
                    self.minusBracket += 1
                self.nextToken()

                x = self.s0()

                self.minus = False
                if self.minusBracket >= 0:
                    self.minusBracket -= 1
                if self.token != None and self.token in "\"'":
                    self.quote = False
                self.nextToken()
                x = self.add(x, self.s1())
            elif self.token not in "()|\"'":
                if self.token == "-":
                    self.minus = True
                else:
                    x = self.new()
                self.nextToken()
                x = self.add(x, self.s1())
        return x

    def new(self):
        x = self.token
        if self.quote:
            x = '"' + x
        if self.minus or self.minusBracket > 0:
            self.minus = False
            x = "-" + x
        return [[x]]

    def add(self, x, y):
        res = []
        if len(x) == 0:
            res = y
        elif len(y) == 0:
            res = x
        else:
            for xx in x:
                for yy in y:
                    res.append(xx + yy)
        return res
       
    def parse(self, query):
        self.minus = False
        self.minusBracket = 0
        self.quote = False
        self.query = query.strip().replace(",", " ").replace("&", " ").replace("+", " ").replace(" -", " - ").replace('"', ' " ').replace("|", " | ").replace("(", " ( ").replace(")", " ) ").split()
        self.nextToken()
        return self.s0()

def main():
    import sys
    par = Parser()
    while True:
        l = sys.stdin.readline()
        if not l:
            break
        print par.parse(l)
        
if __name__ == "__main__":
    main()
