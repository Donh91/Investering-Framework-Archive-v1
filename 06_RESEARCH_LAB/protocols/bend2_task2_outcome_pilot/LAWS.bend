import Base
import ./job.bend as Job

law censored_never_scoreable:
  {Job.scoreable(Job.Censored{}) == False{} : Bool}

law unknown_never_scoreable:
  {Job.scoreable(Job.Unknown{}) == False{} : Bool}

law matured_without_binding_never_scoreable:
  {Job.scoreable(Job.MaturedUnbound{}) == False{} : Bool}

law unscoreable_matured_never_scoreable:
  {Job.scoreable(Job.MaturedUnscoreable{}) == False{} : Bool}

law bound_hit_scoreable:
  {Job.scoreable(Job.BoundMaturedHit{}) == True{} : Bool}

law bound_miss_scoreable:
  {Job.scoreable(Job.BoundMaturedMiss{}) == True{} : Bool}

law no_counter_based_independent_validation:
  for outcome: Job.Outcome
  {Job.independently_validated_by_counter(outcome) == False{} : Bool}
