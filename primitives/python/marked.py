"""marked — thin wrapper sugar over the provenance law. The law lives in provenance.py."""
from provenance import combine_provenance, make_meta

def mark(value, **meta_input):
    return {'value': value, 'meta': make_meta(**meta_input)}

def unwrap(marked):
    return marked['value']

def meta_of(marked):
    return marked['meta']

def derive(inputs, fn, **meta_override):
    value = fn(*[unwrap(i) for i in inputs])
    combined = combine_provenance(*[meta_of(i) for i in inputs])
    merged = dict(combined)
    merged.update(meta_override)
    merged['derived_from_mock'] = combined['derived_from_mock'] or bool(meta_override.get('derived_from_mock'))
    return {'value': value, 'meta': merged}
