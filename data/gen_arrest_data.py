import openpolicedata as opd
import pandas as pd
import os

table = 'ARRESTS'

src = opd.Source('Fairfax County')
years = src.get_years(table)

year_col = []
months = []
charges = []
arrests = []

case_cols = ['CaseNum', 'Case Number', 'CaseNumber','SurrogateI']
arrestid_cols = ['ArrestID', 'Arrest ID', 'Arrest_ID']
for y in years:
    print(y)
    t = src.load(table ,y)
    t.standardize()

    t.table['MONTH'] = t.table['DATE'].dt.month
    t.table['YEAR'] = t.table['DATE'].dt.year

    c1 = [x for x in case_cols if x in t.table]
    c2 = [x for x in arrestid_cols if x in t.table]

    assert len(c1)==1

    if len(c2)>1:
        assert(len(c2)==2)
        assert t.table.apply(lambda x: x[c2[0]]==x[c2[1]] or x[c2[0]]!=0 or x[c2[1]]!=0, axis=1).all()

        t.table['ARRESTID_Combo'] = t.table.apply(lambda x: x[c2[0]] if x[c2[0]]!=0 else x[c2[1]], axis=1)
        c2 = ['ARRESTID_Combo']

    assert len(c2)==1

    # A person can have multiple charges at an arrest. These results in multiple rows for the same arrest
    # Only keep one row per arrests which is nominally a unique case number and unique arrest ID, which will uniquely identify each person arrested in a case
    unique1 = ~t.table.duplicated(subset=[c1[0], c2[0]])
    # HOWEVER, many case numbers are null. Keep unique individuals arrested on different days. This is the best we can do for null case numbers
    unique2 = t.table[c1[0]].isnull() & (~t.table.duplicated(subset=['DATE', c2[0]]))

    df = t.table[unique1 | unique2].reset_index()

    print(f'{len(t.table)} Charges and {len(df)} Arrests of {df[c2[0]].nunique()} people')

    vc1 = df[['YEAR','MONTH']].value_counts().reset_index()
    vc2 = t.table[['YEAR','MONTH']].value_counts().reset_index()
    vc = vc1.merge(vc2, on=['YEAR','MONTH'])
    vc = vc.sort_values(['YEAR','MONTH'])

    year_col.extend(vc['YEAR'])
    months.extend(vc['MONTH'])
    charges.extend(vc['count_y'])
    arrests.extend(vc['count_x'])

df = pd.DataFrame({'Year':year_col, 'Month':months ,'Charges':charges, 'Arrests':arrests})
df.to_csv(os.path.join('data', 'fcpd_arrest_totals.csv'), index=False)