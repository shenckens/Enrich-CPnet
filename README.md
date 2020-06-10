# Enrich-CPnet

Code for merging two conditional preference networks (CP-nets).

The first CP-net gets enriched with preferences and/or features from the second CP-net.//


Run enrich.py in a Python 3 terminal.

For explanations and examples, see below.


### JSON example


Every .json must be formatted according to the example below.


```
{ 
  "name" : <"name of the CP-net">,  
  "enriched" : [<list containing strings of other CP-net names already used for enriching>],
  "CPT" : {     
         <"feature_name"> : {         
                             "domain" : [<list containing strings of all feature values>],                            
                             "pref_relations" : {                           
                                               "condition" : [<list of condition(s)>],                                            
                                               "preference" : [<list of preference ordering>],                                             
                                               "regardless" : [<list of regardless value(s)>]                                          
                                              },                                          
                                              {                                              
                                                ...                                               
                                              }                                              
                            },                            
          <feature_name> : {          
                            ...                           
                            },                           
         }     
}
```


NOTE: in the pref_relation section; condition, preference and regardless can be nested representations

For example:

The condtional preference statement:   
```
a; b; (c & d): x2 > (x1 ~ x4) > x3 [e, f]
```

is represented in a json as:           
```
"condition" : ["a", "b", ["c", "d"]]
"preference" : ["x2", ["x1", "x4"], "x3"]                  
"regardless" : ["e", "f"]
```
                                       
Meaning that: 

a nested list in 'condition' corresponds to a conjunctive condition

a nested list in 'preference' corresponds to an indifferent relation (~)

Also:

The order of values in 'preference' represents the perferential order from most preferred to least preferred.

If a conditional preference relation is independent, the condition is set to ```["None"]```

If there is no regardless, it is set to ```["None"]```

If a CP-net is not enriched yet, ```"enriched"``` in the json holds the empty list ```[]```
