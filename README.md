# nth

Expand decimal numbers to word form, and vice versa.

```
> import nth

> nth.decimalize("TWO THOUSAND AND FORTY-FIFTH")
'2045TH'

> nth.decimalize("I live on First St.")
'I live on 1ST St.'
```

**Todo:**
- [ ] Re-do the integer-to functions to have similar signatures and functionality to
  `decimalize`, or better write new functions `cardinalize` and `ordinalize` and behave
  similarly.
- [ ] Selective convertion from one form to another.
