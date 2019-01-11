import yaml
import networkx as nx
from collections import OrderedDict
# Fills dict with None if key opt not found

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def wildcard(pattern,qs):
    match = lambda pattern, word: word[0:len(pattern)-1] == pattern[:-1]
    return [q for q in qs if match(pattern,q)]

# def pattern_expansion(pattern,qs):
#     expansion = []
#     for q in qs:
#         if q[-1] == "*":
#             expansion += wildcard(q,qs)
#     return expansion

def non_expandable(qs):
    return [q for q in qs if q[-1]!='*']

def _getopt(opt, q, qs):
    if opt in qs[q]:
        return qs[q][opt]
    else:
        return []

def sequence_expansion(patterns,qs):
    pat = []
    for p in patterns:
        if p[-1]=="*":
            pat += wildcard(p,qs)
        else:
            pat.append(p)
    return pat

def _getpat(opt,q,qs):
    v = _getopt(opt,q,qs)
    return sequence_expansion(v,qs)

def dict_expansion(d, qs):
    return {v: sequence_expansion(d[v],qs) for v in d}
#_getopt = lambda opt, q, qs: qs[opt] if opt in qs[q] else None

class depgraph():
    def __init__(self,qdeps,sdeps):
        G = nx.DiGraph()

        self.qdeps = qdeps
        self.sdeps = sdeps
        for q in self.qdeps:
            if self.qdeps[q]:
                G.add_edges_from([(dep,q) for dep in self.qdeps[q]])
        for q in self.sdeps:
            if self.sdeps[q]:
                G.add_edges_from([(q,dep) for dep in self.sdeps[q]])

        self.qgraph = G

    def resolve(self,q):
        prec = []; succ = []
        if self.qdeps[q]:
            for p in self.qdeps[q]:
                if p not in prec:
                    H = nx.shortest_path(self.qgraph,p,q)
                    prec += H
                    print(p,H)
        else:

            prec = [q]
        if self.sdeps[q]:
            for p in self.sdeps[q]:
                if p not in succ:
                    H = nx.shortest_path(self.qgraph, q,p)
                    succ += H
        solution = prec + succ
        return unique(solution)

class questions():
    def __init__(self, raw_qstruct):
        self.raw_qstruct = raw_qstruct

        self.initial = raw_qstruct['conteúdo']
        self.qs = raw_qstruct['questões']
        self.ss = raw_qstruct['seções']

        self.qdeps = {q: _getpat("antecedentes",q,self.qs) + _getpat("cluster",q,self.qs) for q in self.qs}
        self.sdeps = {q: _getpat("descendentes",q,self.qs) + _getpat("cluster",q,self.qs) for q in self.qs}

        self.qdeps = dict_expansion(self.qdeps,self.qs)
        self.sdeps = dict_expansion(self.sdeps,self.qs)

        self.qgraph = depgraph(self.qdeps, self.sdeps)


    def compile(self,_as, q):
        assert q in self.qs, "{} not in self.qs".format(q)
        if 'texto' in self.qs[q]:
            txt = self.qs[q]['texto']
        else: txt = "FALTA TEXTO"
        if 'tipo-resposta' in self.qs[q]:
            tipo = self.qs[q]['tipo-resposta']
        else: tipo = "escolha única"
        return  {'texto':txt,'tipo-resposta': tipo,'resposta': self.answer(_as,q)}
    def section_contents(self,_as, s):

        contents = sequence_expansion(self.ss[s]['conteúdo'],self.qs)
        resolved = []
        for q in contents:
            resolved += self.qgraph.resolve(q)

        return {q: self.compile(_as, q) for q in unique(resolved)}

    def answer(self,_as,q):
        t = self.qs[q]['tipo-resposta'] if 'tipo-resposta' in self.qs[q] else 'escolha única'
        r = self.qs[q]['respostas'] if 'respostas' in self.qs[q] else [""]

        if isinstance(r,list):
            return r
        elif (t,r) in _as.asdict:
            return _as.asdict[(t,r)]
        else:
            return r

class answers():
    def __init__(self,raw_as):
        self.raw_as = raw_as
    @property
    def asdict(self):
        keys = []
        for atype in self.raw_as:
            keys += [(atype, aname) for aname in self.raw_as[atype]]

        return {key: self.raw_as[key[0]][key[1]] for key in keys}

class FPQ():
    def __init__(self, qfile, afile):
        with open(qfile, 'r', encoding = 'utf8') as handle: raw_qstruct = yaml.load(handle)
        with open(afile, 'r', encoding = 'utf8') as handle: raw_as = yaml.load(handle)

        self.meta = raw_qstruct['conteúdo']
        self.astruct = answers(raw_as)
        self.qstruct = questions(raw_qstruct)

    def assemble(self):
        print(self.meta['título'])
        ssq = set()
        ssd = OrderedDict()
        # Para evitaar que a mesma questão apareça em mais de uma seção

        for s in self.meta['seções']:
            sequence = self.qstruct.section_contents(self.astruct,s).keys()
            ssd[s] = [x for x in sequence if not (x in ssq or ssq.add(x))]
            ssq = ssq.union(set(sequence))
        missing = set(self.qstruct.qs.keys()).difference(ssq)
        if missing:
            print(missing)
            self.qstruct.ss.update({'Outros':  {'título': 'Outros', 'conteúdo':list(missing)}})
            ssd['Outros'] = list(missing)
        return ssd
    def export(self):
        contents = self.assemble()
        print(contents.keys())
        #return contents
        output = {s:\
                    {q: self.qstruct.compile(self.astruct, q) for q in contents[s]}\
                 for s in contents}
        return output
