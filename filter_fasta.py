#!/usr/bin/env python3
# Roger Volden

'''
This is going to take a directory with my isotype files, which contain
a header as well as an isotype.
It will take the header and find it in that particular cell's fasta
file, which should be in the demuxed directory.
It will output a fasta file with the relevant reads.

I'm adding on the functionality of getting the lines from the psl files
as well because it makes more sense to do it here than to write another
script. Because of this, I might also ditch the separate script for the
subreads, but that might be a bit more challenging.

python3 filter_fasta.py . ../misc/41_post_flc.fasta
'''

import sys
import os
import mappy
from progress.bar import Bar

def readFasta(inFile):
    '''Reads in FASTA files, returns a dict of header:sequence'''
    readDict = {}
    for name,seq,qual in mappy.fastx_read(inFile):
        readDict[name]=seq
    return readDict

def readSAM(inFile):
    '''Reads in a sam file and returns a dict of header:sam line'''
    headers = []
    for line in open(inFile):
        line = line.rstrip()
        header = line.split('\t')[0]
        headers.append(header)
    return headers

def readFastq(seqFile):
    readDict={}
    for name,seq,qual in mappy.fastx_read(seqFile):
        root_name=name.split('_')[0]
        if root_name not in readDict:
            readDict[root_name]=[]
        readDict[root_name].append((name,seq,qual))
    return readDict

def main():
    sub_path1=sys.argv[1]
    sub_path2=sys.argv[2]
    fileList = os.listdir(sub_path2)
    fileList = [x for x in fileList if x.endswith('.sam')]
    b = Bar('Processing files', max=len(fileList))
    for file in fileList:
        fastaDict=readFasta(sub_path1+'/'+file.split('-')[0]+'.fasta')
        fastqDict=readFastq(sub_path1+'/'+file.split('-')[0]+'_subs.fastq')
        headers = readSAM(sub_path2+'/'+file)
        faName = sub_path2+'/'+file.split('.')[0] + '.fasta'
        fqName = sub_path2+'/'+file.split('.')[0] + '.subreads.fastq'
#        print(file)
        faOut = open(faName, 'w+')
        for header in headers:
            faOut.write('>' + header + '\n' + fastaDict[header] + '\n')
        faOut.close()
        fqOut = open(fqName, 'w+')
        for header in headers:
            header=header.strip().split('_')[0]
            if header in fastqDict:
                for name,seq,qual in fastqDict[header]:
                    fqOut.write('@' + name + '\n' + seq + '\n+\n'+qual+'\n')

        b.next()

    b.finish()

main()
