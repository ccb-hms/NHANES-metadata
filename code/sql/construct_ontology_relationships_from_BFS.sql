/*

We're going to run breadth first search to identify all concepts

that are reachable from every possible starting point in the graph.

*/



-- first pull out the parent / child relationships

SELECT 

R.CUI1 AS Cui, 

R.CUI2 AS ParentCui 

INTO #tmpCuiRelationships 

FROM MRREL R 

WHERE 

CUI1 != CUI2 

AND REL='PAR'

GROUP BY R.CUI1, R.CUI2



-- we will run BFS starting from every concept that appears as a parent somewhere

SELECT CUI2 
AS Cui

INTO

#tmpCuisThatAppearAsParents

FROM MRREL

WHERE REL='PAR'

GROUP BY CUI2



-- it's ugly, but it works: iterate over that set of parent vertices

DECLARE @CurrentSourceCui 
varchar(8)

DECLARE cCuis 
CURSOR

FOR SELECT * 
FROM #tmpCuisThatAppearAsParents



OPEN cCuis

FETCH 
NEXT FROM cCuis 
INTO @CurrentSourceCui



DECLARE @ConceptSet 
TABLE (

Cui varchar(8)

)



DECLARE @nConcepts 
int

DECLARE @nConceptsUpdate 
int



IF 
OBJECT_ID('ConceptMapping', 
'U') IS NOT NULL

DROP 
TABLE ConceptMapping

CREATE 
TABLE ConceptMapping (SourceCui
varchar(8), DestinationCui
varchar(8))



WHILE @@FETCH_STATUS = 
0

BEGIN


-- start fresh for this source concept

DELETE 
FROM @ConceptSet



-- initialize the set of concepts

INSERT INTO @ConceptSet (Cui) 
VALUES (@CurrentSourceCui)



SET @nConcepts=0

SET @nConceptsUpdate=1


-- while we saw something new on the last iteration

WHILE @nConcepts != @nConceptsUpdate

BEGIN


-- remember how many distinct concepts have been seen so far

SELECT @nConcepts=COUNT(DISTINCT Cui)
FROM @ConceptSet



-- add everything that we can get to from the current set

INSERT INTO @ConceptSet

SELECT R.Cui 
FROM #tmpCuiRelationships R INNER JOIN @ConceptSet S
ON R.ParentCui=S.Cui



-- determine whether we saw anything new

SELECT @nConceptsUpdate=COUNT(DISTINCT Cui)
FROM @ConceptSet

END



-- update the full mapping table

INSERT INTO ConceptMapping

SELECT @CurrentSourceCui, S.Cui 
FROM @ConceptSet S GROUP BY S.Cui



-- next source concept

FETCH 
NEXT FROM cCuis 
INTO @CurrentSourceCui

END



CLOSE cCuis

DEALLOCATE cCuis



-- add loopbacks for CUIs that were not listed as parents

INSERT INTO ConceptMapping (SourceCui, DestinationCui)

SELECT CUI, CUI 
FROM MRCONSO C WHERE C.CUI 
NOT IN (SELECT SourceCui
FROM ConceptMapping) 
GROUP BY C.CUI



CREATE 
CLUSTERED INDEX idxConceptMappingSourceCuiDestinationCui
ON ConceptMapping (SourceCui, DestinationCui)

CREATE 
NONCLUSTERED INDEX idxConceptMappingDestinationCuiSourceCui
ON ConceptMapping (DestinationCui, SourceCui)