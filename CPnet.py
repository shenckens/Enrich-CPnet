import json


class CPnet(object):


    def __init__(self, CPN_path):
        """Initialise the CP-net object.
           CPN_path - path containing the CP-net json file."""
        if not CPN_path.lower().endswith('.json'):
            raise Exception("Path must lead to '.json' file.")
        with open(CPN_path) as f:
            self.CPN = json.load(f)
        self.name = self.CPN["name"]
        self.features = set([F for F in self.CPN["CPT"]])
        self.domains = {feature:(set([val for val in self.CPN["CPT"]\
                        [feature]["domain"]])) for feature in self.features}


    def get_name(self):
        """Return the name of the CP-net."""
        return self.name


    def get_features(self):
        """Return the set of features that exist in the CP-net."""
        return self.features


    def get_enrichments(self):
        """Returns how many times the CP-net was enriched."""
        # return self.enrichments
        return len(self.CPN["enriched"])


    def get_CPT(self, feature):
        """Returns the conditional preference table for a given features
           in the CP-net. Returns the conditional preference tables for all
           features in the CP-net if no feature is given."""
        if feature in self.features:
            return self.CPN["CPT"][feature]
        raise Exception("Feature '{}' not in CP-net.".format(feature))


    def get_domain(self, feature):
        """Returns the domain of feature values."""
        return self.domains[feature]


    def add_domain(self, feature, other_domain):
        """Adds the unique values in a feature domain coming from another CPN
           to its own feature domain."""
        for value in other_domain:
            self.domains[feature].add(value)
            if not value in self.CPN["CPT"][feature]["domain"]:
                self.CPN["CPT"][feature]["domain"].append(value)
        pass


    def get_preference_relation(self, feature, condition):
        """Returns the prefence relation over feature values given a condition
           ('None' for independent preference, list for conjunction)."""
        if isinstance(condition, list):
            condition = sorted(condition)
        for pref_relation in self.get_CPT(feature)["pref_relations"]:
            check = pref_relation["condition"][0]
            if isinstance(check, list):
                check = sorted(check)
            if check == condition:
                return pref_relation
        raise Exception("Condition '{}' not in preference relations."\
                        .format(condition))


    def get_preference(self, feature, condition):
        """Returns the preference ordering given a condition."""
        return self.get_preference_relation(feature, condition)["preference"]


    def get_regardless(self, feature, condition):
        """Returns the regardless given a condition."""
        return self.get_preference_relation(feature, condition)["regardless"]


    def add_feature(self, feature):
        """Adds a feature with an empty CPT(feature) to the CP-net.
           Returns False if the feature already existed in the CP-net."""
        if feature in self.features:
            return False
        self.CPN["CPT"][feature] = {"domain":[], "pref_relations":[]}
        self.features.add(feature)
        self.domains[feature] = set()
        pass


    def new_preference_relation(self, feature, condition):
        """Adds a new preference relation with an unique condition to an
           existing feature."""
        CPT = self.get_CPT(feature)
        CPT["pref_relations"].append({"condition": [condition], \
                                      "preference": [], "regardless": []})
        return CPT["pref_relations"][-1]


    def remove_preference_relation(self, feature, pref_relation):
        """Removes a conditional preference relation."""
        self.CPN["CPT"][feature]["pref_relations"].remove(pref_relation)
        pass


    def get_conditions(self, feature):
        """Returns all conditions given a feature."""
        conditions = []
        for pref_relation in self.get_CPT(feature)["pref_relations"]:
            if pref_relation["condition"][0] != "None":
                conditions.append(pref_relation["condition"][0])
        return conditions


    def set_name(self, name):
        """Changes the name."""
        self.CPN["name"] = name
        self.name = name
        pass


    def increase_enrichments(self, other):
        """Increments the enrichments counter."""
        if not other.get_name() in self.CPN["enriched"]:
            self.CPN["enriched"].append(other.get_name())
        pass


    def complete_merge(self, feature, condition, preference, regardless):
        """Creates a entire new conditional preference relation given
           a condition. Takes a preference relation and regardless."""
        pref_relation = self.new_preference_relation(feature, condition)
        pref_relation["preference"] = preference
        pref_relation["regardless"] = regardless
        pass


    def partial_merge(self, feature, condition, preference, regardless):
        """Parially merges values in a preference ordering from another CPN to
           its own CPN. Creates a new indifferent preference ordering if there
           is no index to insert."""
        pref_1 = self.get_preference_relation(feature, condition)["preference"]
        pref_2 = preference
        for val_2 in pref_2:
            if not val_2 in pref_1:
                val_2_index = pref_2.index(val_2)
                right_set = set(pref_2[val_2_index:]).intersection(set(pref_1))
                left_set = set(pref_2[:val_2_index]).intersection(set(pref_1))
                # Insert value and check indifference
                check = self.insert_value(pref_1, val_2, left_set, right_set)
                if check:
                    for val in check:
                        new = self.new_preference_relation(feature, condition)
                        new["preference"] = [list([str(val), str(val_2)])]
                        new["regardless"] = regardless
        pass


    def insert_value(self, preference, value, left_set, right_set):
        """Inserts a value coming from the partial merge function at the
           right index. Returns the index to insert.
           Otherwise returns a list of indifferent values."""
        # Check if value needs to be insterted.
        for left in left_set:
            for right in right_set:
                if preference.index(left) > preference.index(right):
                    return 0
        i_l = 0
        for i in range(len(preference)):
            if preference[i] in left_set:
                i_l = i
            if preference[i] in right_set:
                i_r = i
                if len(left_set) == 0:
                    if i_r == 0:
                        preference.insert(0, value)
                        break
                    return preference[:i_r]
                if (i_r - i_l) == 1:
                    preference.insert(i_r, value)
                    break
                else:
                    return preference[i_l:i_r]
            if len(right_set) == 0 and preference[-1] == preference[i]:
                preference.append(value)
                break
        return 0


    def decompose_multiple(self, feature, pref_relation):
        preference = pref_relation["preference"]
        regardless = pref_relation["regardless"]
        for _ in pref_relation["condition"][:-1]:
            condition = pref_relation["condition"].pop(0)
            new = self.new_preference_relation(feature, condition)
            new["preference"] = list(preference)
            new["regardless"] = list(regardless)
        pass


    def decompose_independent(self, feature, pref_relation):
        """Decomposes an independent preference relation to single condition
           preference relations."""
        used = self.get_conditions(feature)
        preference = pref_relation["preference"]
        regardless = pref_relation["regardless"]
        for f in self.features:
            if f == feature:
                continue
            for condition in self.domains[f]:
                if not condition in used:
                    new = self.new_preference_relation(feature, condition)
                    new["preference"] = list(preference)
                    new["regardless"] = list(regardless)
        pass


    def decompose(self):
        """Decomposes every preference relation where possible."""
        for feature in self.features:
            for pref_relation in self.get_CPT(feature)["pref_relations"]:
                if len(pref_relation["condition"]) > 1:
                    self.decompose_multiple(feature, pref_relation)
        for feature in self.features:
            for pref_relation in self.get_CPT(feature)["pref_relations"]:
                if pref_relation["condition"][0] == "None":
                    self.decompose_independent(feature, pref_relation)
                    self.remove_preference_relation(feature, pref_relation)
        pass



    def check_regardless(self, feature, condition):
        """Checks regardless for every conditional preference relation
           and fills them in where needed."""
        # Still do to ?

        pass


    def recompose(self):
        """Recomposes every feature in an enriched CPN where possible."""
        # Add all conditions with equal preference together
        for feature in sorted(self.features):
            prefs = self.get_CPT(feature)["pref_relations"]
            if len(prefs) > 1:
                for pref in prefs:
                    for check in prefs[1:]:
                        if check["preference"] == pref["preference"] and\
                           check != pref:
                            pref["condition"].append(check["condition"][0])
                            self.remove_preference_relation(feature, check)
                            return self.recompose()
        # Check if conjunction of conditions means independence
        for feature in self.features:
            independent = True
            all_domains = []
            for f in self.features.difference(set(feature)):
                all_domains.extend(list(self.get_domain(f)))
            prefs = self.get_CPT(feature)["pref_relations"]
            for pref in prefs:
                for check in all_domains:
                    if not check in pref["condition"]:
                        independent = False
                if independent:
                    pref["condition"] = ["None"]
        pass



    def make_json(self):
        """Creates a new .json containing the enriched CPN."""
        CPN = self.CPN
        name = "{}_{}.json".format(self.get_name(), self.get_enrichments())
        with open(name, "w") as f:
            json.dump(CPN, f, indent=4)
        pass


    def __str__(self):
        """Returns the string representation of the CP-net object."""
        string = []
        string.append("\n<{}>".format(str(self.name)))
        if self.get_enrichments() > 0:
            string.append(" ({}x enriched)".format(str(self.get_enrichments())))
        string.append("\n")
        for feature in sorted(self.features):
            string.append("\n{}:\n\t".format(feature))
            for pref_relation in self.CPN["CPT"][feature]["pref_relations"]:
                if pref_relation["condition"][0] != "None":
                    for i in pref_relation["condition"]:
                        if isinstance(i, list):
                            string.append("(")
                            for j in i:
                                string.append(str(j)), string.append(" & ")
                            string[-1] = ")"
                            string.append("; ")
                            continue
                        string.append(str(i)), string.append("; ")
                    string[-1] = "  :  "
                for value in pref_relation["preference"]:
                    if isinstance(value, list):
                        string.append("(")
                        for i in value:
                            string.append(str(i)), string.append(" ~ ")
                        string[-1] = ")"
                        string.append(" > ")
                        continue
                    string.append(str(value)), string.append(" > ")
                if pref_relation["regardless"][0] != "None":
                    string[-1] = " ["
                    for i in pref_relation["regardless"]:
                        string.append(str(i)), string.append(", ")
                    string[-1] = "]"
                else:
                    del string[-1]
                string.append("\n"), string.append("\t")
            del string[-1]
        return "".join(string)
