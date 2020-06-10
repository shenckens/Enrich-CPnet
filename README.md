# Thesis-code

Code for merging two conditional preference networks (CP-nets).

The first CP-net gets enriched with preferences and/or features from the second CP-net.


Run enrich.py in a Python 3 terminal.

For explanations and examples, see below.


############

JSON example

############


Every .json is formatted according to the example below.


```
{ 
  name : <name of the CP-net>,  
  enriched : <list of other CP-nets already used for enriching>,
  CPT : {     
         <feature_name> : {         
                             domain : <list of all feature values>                            
                             pref_relation : {                           
                                               condition : <list of condition(s)>                                            
                                               preference : <list of preference ordering>                                             
                                               regardless : <list of regardless values>                                          
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
condition : [a, b, [c, d]]
preference : [x2, [x1, x4], x3]                  
regardless : [e, f]
```
                                       
Meaning that: 

a nested list in 'condition' corresponds to a conjunctive condition

a nested list in 'preference' corresponds to an indifferent relation (~)


The order of values in 'preference' represents the perferential order from most preferred to least preferred.
