Set t(*) Time periods /
'2007',
'2010',
'2015',
'2020',
'2025',
'2030',
'2035',
'2040',
'2045',
'2050' /;

Set r(*) All regions /
'BJ',
'TJ',
'HE',
'LN',
'SH',
'JS',
'ZJ',
'FJ',
'SD',
'GD',
'HI',
'SX',
'NM',
'JL',
'HL',
'AH',
'JX',
'HA',
'HB',
'HN',
'GX',
'CQ',
'SC',
'GZ',
'YN',
'SN',
'GS',
'QH',
'NX',
'XJ' /;

set foo / c, ptcarb, CHN, egycons, nhw_share /;
parameters report(*,*,*), egyreport2(*,*,*,*), nucl(r,t), hydr(r,t), wind(r,t), solar(r,t);

execute_load '%file%.gdx', report, egyreport2, nucl, hydr, wind, solar;

set e / COL, GAS, OIL, NUC, HYD, WND, SOL /;
set fe(e) / COL, GAS, OIL /;

parameter pe_t(e,r,t), ptcarb_t(t), cons_t(r,t), nhw_share(r,t), nhw_share_CN(t);

display report;

loop(t,
  ptcarb_t(t) = report('ptcarb',t,'CHN');
  nhw_share_CN(t) = report('nhw_share',t,'CHN');
  loop(r,
    pe_t(fe,r,t) = egyreport2('egycons',t,fe,r);
    pe_t('NUC',r,t) = nucl(r,t);
    pe_t('HYD',r,t) = hydr(r,t);
    pe_t('WND',r,t) = wind(r,t);
    pe_t('SOL',r,t) = solar(r,t);
    nhw_share(r,t) = report('nhw_share',t,r);
    cons_t(r,t) = report('c',t,r);
  );
);

option kill=report;
option kill=egyreport2;
option kill=nucl;
option kill=hydr;
option kill=wind;
option kill=solar;
option kill=fe;
option kill=foo;

execute_unload '%file%_extra.gdx';
