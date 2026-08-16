# Expanded Pharmaceutical Sample Protocol v0.1

## Status

Pre-specified before component-level data collection for the expanded sample.

This protocol defines how therapeutic families and medicinal products will be
selected for the expanded empirical analysis.

Packaging topology, container type, closure type, supplier identity,
manufacturing site convergence, or any previously observed component-network
result MUST NOT be used to determine whether a candidate family or product is
included.

The original 9-product parenteral acid-suppression dataset remains a frozen
proof-of-concept sample and is not used to select the expanded sample.

---

# 1. Research objective

The expanded sample evaluates whether the component-level convergence observed
in the proof-of-concept persists outside the original parenteral
acid-suppression family.

The primary empirical question is:

> Do therapeutically distinct medicinal alternatives remain structurally
> diversified when the analysis moves from active ingredient identity to
> deliverable-product component dependencies?

The expanded analysis will separately evaluate:

1. exact physical component convergence;
2. parent-component convergence;
3. terminal component-family convergence;
4. evidence-supported component coverage;
5. sensitivity to incomplete public documentation;
6. dosage-form conditioning of observed convergence.

Observed convergence does not by itself establish:

- supplier identity;
- mandatory dependence;
- non-substitutability;
- common failure mode;
- disruption probability;
- shortage probability;
- national supply-chain criticality.

---

# 2. Unit of sampling

The primary sampling unit is the therapeutic family.

A therapeutic family is a pre-defined set of active ingredients that can
reasonably act as therapeutic alternatives within a specified clinical context.

The product is the secondary sampling unit.

The physical component is an analytical dependency unit and MUST NOT be used
as a sampling criterion.

---

# 3. Expanded-sample target

The target expanded sample is:

- up to 8 therapeutic families;
- at least 6 families if the eligible public-data universe permits;
- approximately 4–8 medicinal products per family;
- multiple active ingredients per family;
- multiple marketing-authorisation holders or manufacturers where naturally
  present in the eligible universe.

The final product count is not fixed in advance because the number of
publicly documentable eligible products differs between therapeutic families.

No family will be expanded or reduced because its packaging structure appears
scientifically interesting after inspection.

---

# 4. Route/form strata

Candidate therapeutic families will be classified before packaging extraction
into two broad design strata.

## Stratum H — route/form-homogeneous families

Therapeutic alternatives are predominantly represented by the same broad
administration route and pharmaceutical-form family.

Examples of broad route/form classes include:

- parenteral sterile;
- oral solid;
- oral liquid;
- inhaled;
- topical;
- ophthalmic.

The purpose of this stratum is to test whether component convergence persists
even after broad dosage-form differences are conditioned out.

## Stratum D — route/form-diverse families

Therapeutically relevant alternatives are represented by more than one broad
route or pharmaceutical-form family.

The purpose of this stratum is to provide a structural control for
dosage-form-conditioned convergence.

A family is assigned to H or D using clinical/formulation information before
component-level packaging extraction.

The assignment MUST NOT use container, stopper, seal, blister, vial, bottle,
ampoule, syringe, carton, or other component information.

---

# 5. Family eligibility criteria

A therapeutic family is eligible only when all of the following are satisfied.

## 5.1 Clinical criterion

A defensible clinical or pharmacological basis exists for grouping the active
ingredients as therapeutic alternatives within a defined clinical context.

The evidence basis must be recorded.

ATC membership alone is not sufficient when it does not establish meaningful
therapeutic comparability.

## 5.2 Active-ingredient multiplicity

Preferred eligibility:

- at least 3 distinct active ingredients.

Fallback eligibility:

- 2 active ingredients may be retained when the family otherwise provides a
  strong and well-documented therapeutic comparison.

Families with only one active ingredient are excluded.

## 5.3 Product multiplicity

Preferred eligibility:

- at least 6 eligible medicinal products across the family.

Fallback eligibility:

- at least 4 products when the public universe does not provide 6 products.

## 5.4 Public-document criterion

The products must belong to a public medicinal-product universe that permits
product identity to be frozen independently of packaging findings.

A product is not excluded merely because its current KÜB/KT cannot subsequently
be recovered.

Such products remain in the frozen sample and are coded as unresolved when
appropriate.

This preserves missing-document uncertainty instead of creating
post-selection bias.

## 5.5 Human medicinal products

The analysis is restricted to human medicinal products.

Veterinary products are excluded.

---

# 6. Family exclusion criteria

A family is excluded before packaging extraction when:

1. therapeutic comparability cannot be defended;
2. fewer than two active ingredients are available;
3. the product universe cannot be reproducibly identified;
4. the family definition depends on packaging or supply-chain information;
5. eligibility would require knowledge obtained from the component audit;
6. the family consists primarily of products whose identity cannot be
   distinguished in the public data source.

No family may be excluded because preliminary component convergence is low.

No family may be included because preliminary component convergence is high.

---

# 7. Candidate-family registry

Before component extraction, every candidate family must be entered in a
candidate-family registry containing at minimum:

- family_id;
- family_name;
- clinical_context;
- eligibility_basis;
- evidence_source;
- route_form_stratum;
- n_candidate_active_ingredients;
- n_candidate_products;
- eligibility_status;
- exclusion_reason, if applicable;
- reviewer_note.

The registry itself is frozen before component-level extraction begins.

---

# 8. Deterministic family selection

If the number of eligible families exceeds the target, families will not be
manually selected based on subjective interest.

Eligible families will be selected deterministically within each route/form
stratum.

The intended allocation is:

- 4 families from Stratum H;
- 4 families from Stratum D;

subject to the available eligible universe.

If one stratum contains fewer than four eligible families, the unused places
may be filled from the other stratum.

Selection order will be generated from a deterministic SHA-256 hash based on:

    study_seed || family_id

with the frozen study seed:

    pharma_resilience_tr_expansion_v0_1

Families will be sorted by the resulting hash value.

This creates a reproducible selection that is independent of packaging
topology and analyst preference.

---

# 9. Product selection within a family

All clearly eligible products should be retained when the family contains
eight or fewer products.

When more than eight products are eligible, selection must preserve
active-ingredient representation.

The following procedure will be used:

1. retain at least one product for every eligible active ingredient;
2. preferentially retain two products per active ingredient where possible;
3. if additional sampling is necessary, use deterministic SHA-256 ordering
   based on:

       study_seed || family_id || product_id

4. stop at a target maximum of eight products per family unless a documented
   methodological reason requires the complete family universe.

Packaging information is prohibited from the product-selection process.

Manufacturer/site information is not used to select products.

---

# 10. Frozen product universe

After therapeutic-family and product selection, the expanded product universe
is frozen.

Subsequent failure to retrieve a KÜB, KT, packaging description, or site record
does not automatically remove the product.

Instead, the relevant observation is recorded as:

- explicit;
- absent;
- unresolved;
- conflict;

using the existing evidence semantics.

This rule is designed to prevent complete-case selection bias.

---

# 11. Component extraction

Only after the expanded product universe is frozen will component evidence be
collected.

The existing component ontology remains the starting ontology.

Observed evidence may include:

- primary container;
- solvent container;
- closure;
- seal;
- delivery device;
- secondary packaging where explicitly in scope;
- other pre-defined physical component classes.

Raw source wording must be preserved.

Normalisation must be traceable to source evidence.

No component may be invented from pharmaceutical-form knowledge alone.

---

# 12. Resolution hierarchy

The existing multiresolution logic is retained.

## R0 — exact component

Exact normalised physical component class.

## R1 — immediate parent

One observed/pre-defined ontology parent step.

## R2 — terminal family

Highest supported terminal physical component family under the frozen ontology.

Changes in convergence between R0, R1 and R2 are treated as resolution
sensitivity, not automatically as increased physical fragility.

---

# 13. Primary expanded-sample outcomes

The following outcomes are pre-specified.

## 13.1 Cross-ingredient component convergence

For component c:

    number of products represented;
    number of active ingredients represented.

## 13.2 Existential ingredient-pair overlap

For active ingredients a and b at resolution r:

    w_ab(r) = |C_a(r) ∩ C_b(r)|

This is a structural overlap measure.

It does not establish mandatory dependence.

## 13.3 Documentary component support

For active ingredient a and component c:

    q_ac = m_ac / n_a

where:

- m_ac = frozen products with explicit documentary support for component c;
- n_a = all frozen products for active ingredient a.

## 13.4 Evidence-weighted pair overlap

For active ingredients a and b:

    S_ab(r) = Σ_c min(q_ac(r), q_bc(r))

This reflects documented frozen-sample component overlap.

## 13.5 Unresolved-product sensitivity

Products lacking any explicit component evidence are retained.

Componentwise unresolved sensitivity envelopes may be calculated.

These envelopes MUST NOT be described as jointly feasible physical upper
bounds.

---

# 14. Family-level analysis

The expanded sample will be analysed at both:

1. pooled level;
2. therapeutic-family level.

A pooled convergence signal is insufficient by itself.

For each family, the analysis must report:

- number of products;
- number of active ingredients;
- evidence coverage;
- exact-resolution overlap;
- parent-resolution overlap;
- terminal-resolution overlap;
- unresolved evidence burden.

This prevents one large family from silently driving the full result.

---

# 15. Dosage-form conditioning test

The expanded design explicitly evaluates whether convergence is explained
primarily by broad route/form similarity.

Results from Stratum H and Stratum D will therefore be reported separately.

The key comparison is not a significance test alone.

The analysis will inspect whether:

- convergence persists within route/form-homogeneous families;
- convergence substantially disappears in route/form-diverse families;
- specific families contradict the aggregate trend.

Discordant families are analytically important and must not be removed.

---

# 16. Negative and null results

The study does not require every family to exhibit common component
convergence.

Families showing:

- little overlap;
- decreasing overlap;
- highly diversified component structures;
- incomplete evidence;
- no cross-ingredient component convergence

remain valid results.

Such families function as natural structural contrasts and must be retained.

---

# 17. Prohibited post-selection actions

After family selection is frozen, the following actions are prohibited unless
documented as protocol deviations:

- replacing a family because its result is uninteresting;
- replacing an unresolved product with an easier product;
- adding a product because it creates a compelling convergence pattern;
- dropping a product because it weakens convergence;
- redefining component classes to merge desired results;
- redefining therapeutic families after seeing packaging topology;
- using supplier/manufacturer information to retroactively alter sampling.

---

# 18. Protocol deviations

Any deviation from this protocol must be recorded with:

- date;
- affected family/product;
- original rule;
- reason for deviation;
- whether packaging/component results were already known;
- expected direction of possible bias.

Protocol deviations are not silently overwritten.

---

# 19. Relationship to the original proof of concept

The original 9-product parenteral acid-suppression sample remains a separate
developmental proof of concept.

It demonstrated that:

- product-component graphs can be constructed from public evidence;
- cross-ingredient component convergence can be detected automatically;
- convergence is resolution-sensitive;
- incomplete public documentation materially affects interpretation.

It is not treated as an independent confirmatory sample.

The expanded sample is used to evaluate whether those observations generalise.

---

# 20. Next locked steps

After this protocol is committed:

1. create the candidate-family registry schema;
2. identify candidate therapeutic families without inspecting packaging;
3. audit clinical eligibility;
4. assign H/D route-form strata;
5. freeze the eligible-family registry;
6. apply deterministic family selection;
7. freeze selected products;
8. only then begin component extraction.

Packaging data must not be inspected during Steps 1–7 except where unavoidable
for ordinary product identification, and any accidental exposure must be noted.