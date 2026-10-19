import Base

# SHADOW MODEL ONLY. Each constructor is an externally established
# classification, not a parser/verifier of Python market evidence.
type Outcome is Data:
  Censored{}
  Unknown{}
  MaturedUnbound{}
  MaturedUnscoreable{}
  BoundMaturedHit{}
  BoundMaturedMiss{}

def scoreable(outcome: Outcome) -> Bool:
  match outcome:
    case Censored{}: False{}
    case Unknown{}: False{}
    case MaturedUnbound{}: False{}
    case MaturedUnscoreable{}: False{}
    case BoundMaturedHit{}: True{}
    case BoundMaturedMiss{}: True{}

# The current sensor presentation layer must never infer independent
# prospective validation from a counter or a status alone.
def independently_validated_by_counter(outcome: Outcome) -> Bool:
  False{}
