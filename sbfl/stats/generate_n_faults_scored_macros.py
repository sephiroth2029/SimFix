import csv
import argparse
import collections
import inspect

def tally_faults_by_project(file, filter=(lambda project, bug: True)):
  faults = set()
  for row in csv.DictReader(file):
    project, bug = row['Project'], int(row['Bug'])
    if filter(project, bug):
      faults.add((project, bug))
  return collections.Counter(project for project, bug in faults)

parser = argparse.ArgumentParser()
parser.add_argument('artificial_vs_real_scores')
parser.add_argument('exploration_scores')
parser.add_argument('macros_file')
args = parser.parse_args()

projects_bugs_scored = set((row['Project'], int(row['Bug'])) for row in csv.DictReader(open(args.artificial_vs_real_scores)))

avr_n_artificial_faults_scored_by_project = collections.Counter(p for (p,b) in projects_bugs_scored if b>999)
avr_n_real_faults_scored_by_project = collections.Counter(p for (p,b) in projects_bugs_scored if b<=999 and any(afp==p and afb//10**5==b for (afp,afb) in projects_bugs_scored))
avr_n_faults_scored_by_project = avr_n_artificial_faults_scored_by_project + avr_n_real_faults_scored_by_project

with open(args.exploration_scores) as f:
  exploration_n_faults_scored_by_project = tally_faults_by_project(f)

qualifiers_sections_nfaults = {
  ('Real', 'RealVsArtificial'): sum(avr_n_real_faults_scored_by_project.values()),
  ('Artificial', 'RealVsArtificial'): sum(avr_n_artificial_faults_scored_by_project.values()),
  ('', 'RealVsArtificial'): sum(avr_n_faults_scored_by_project.values()),
  ('', 'All'): sum(avr_n_artificial_faults_scored_by_project.values())+sum(exploration_n_faults_scored_by_project.values()),
  ('Real', 'Exploration'): sum(exploration_n_faults_scored_by_project.values())
}
qualifiers_sections_nfaults.update({
  ('Real'+project, 'RealVsArtificial'): n
  for project, n in avr_n_real_faults_scored_by_project.items()
})
qualifiers_sections_nfaults.update({
  ('Artificial'+project, 'RealVsArtificial'): n
  for project, n in avr_n_artificial_faults_scored_by_project.items()
})
qualifiers_sections_nfaults.update({
  ('Real'+project, 'Exploration'): n
  for project, n in exploration_n_faults_scored_by_project.items()
})

with open(args.macros_file, 'w') as f:
  f.write('%% These macros were automatically generated by {}.\n\n'.format(__file__))

  for (qualifier, section), n in sorted(qualifiers_sections_nfaults.items()):
    f.write('\\def\\n{qualifier}FaultsScoredIn{section}Sections{{{n}\\xspace}}\n'.format(qualifier=qualifier, section=section, n=n))
