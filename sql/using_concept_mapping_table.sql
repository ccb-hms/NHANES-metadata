/*

Once the ConceptMapping table is populated, the subtree query problem is now a simple GROUP BY:

*/



USE UmlsSnomedCtIcd9

GO



--SELECT * FROM MRCONSO C WHERE C.STR LIKE '%malignant neoplasm%' AND TS='P' AND STT='PF' ORDER BY CODE



DROP 
TABLE #tmp

SELECT 

M1.DestinationCui,

F.MemberId

INTO #tmp

FROM 

ConceptMapping M1 

INNER JOIN MRCONSO C2 
ON

M1.DestinationCui=C2.CUI

INNER JOIN AetnaDataWarehouse.dbo.FactIcd F
ON 

C2.CODE=F.Icd

WHERE 

(

/*

M1.SourceCui='C0555264' 

OR M1.SourceCui='C0178247' 

OR M1.SourceCui='C0178249' 

OR M1.SourceCui='C0178250' 

OR M1.SourceCui='C0348393' 

OR M1.SourceCui='C0178251'

*/

M1.SourceCui='C0006826'

)

--AND C2.STT='PF' AND C2.TS='P' 

GROUP BY

M1.DestinationCui,

F.MemberId



SELECT T.DestinationCui, 
COUNT(*), C.STR

FROM #tmp T 

INNER JOIN MRCONSO C 
ON T.DestinationCui=C.CUI

GROUP BY T.DestinationCui, C.STR