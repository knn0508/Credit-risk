# Data Dictionary (Agent 02, avtomatik: `python -m src.data.dictionary`)
Kontrakt: data-contract v1.0 · build: 2026-11-24T16:30:16+00:00 · commit: 1cc9ab2 · train 307,511 / test 48,744 sətir · 231 sütun (train).
Grain: 1 sətir = 1 müraciət (`sk_id_curr`). `target` yalnız train-də. Tarixçəsizlik: `<mənbə>_has_history`=0, `*_count`/`*_nunique`=0, digər aqreqatlar NaN.

## Application sütunları
| sütun | dtype | null % | təsvir |
|---|---|---|---|
| sk_id_curr | int64 | 0.0 | ID of loan in our sample |
| target | int64 | 0.0 | Target variable (1 - client with payment difficulties: he/she had late payment more than X days on at least one of the first Y installments of the loan in our sample, 0 - all other cases) |
| name_contract_type | str | 0.0 | Identification if loan is cash or revolving |
| code_gender | str | 0.001 | Gender of the client |
| flag_own_car | str | 0.0 | Flag if the client owns a car |
| flag_own_realty | str | 0.0 | Flag if client owns a house or flat |
| cnt_children | int64 | 0.0 | Number of children the client has |
| amt_income_total | float64 | 0.0 | Income of the client |
| amt_credit | float64 | 0.0 | Credit amount of the loan |
| amt_annuity | float64 | 0.004 | Loan annuity |
| amt_goods_price | float64 | 0.09 | For consumer loans it is the price of the goods for which the loan is given |
| name_type_suite | str | 0.42 | Who was accompanying client when he was applying for the loan |
| name_income_type | str | 0.0 | Clients income type (businessman, working, maternity leave,) |
| name_education_type | str | 0.0 | Level of highest education the client achieved |
| name_family_status | str | 0.0 | Family status of the client |
| name_housing_type | str | 0.0 | What is the housing situation of the client (renting, living with parents, ...) |
| region_population_relative | float64 | 0.0 | Normalized population of region where client lives (higher number means the client lives in more populated region) |
| days_birth | int64 | 0.0 | Client's age in days at the time of application |
| days_employed | float64 | 18.007 | How many days before the application the person started current employment |
| days_registration | float64 | 0.0 | How many days before the application did client change his registration |
| days_id_publish | int64 | 0.0 | How many days before the application did client change the identity document with which he applied for the loan |
| own_car_age | float64 | 65.991 | Age of client's car |
| flag_mobil | int64 | 0.0 | Did client provide mobile phone (1=YES, 0=NO) |
| flag_emp_phone | int64 | 0.0 | Did client provide work phone (1=YES, 0=NO) |
| flag_work_phone | int64 | 0.0 | Did client provide home phone (1=YES, 0=NO) |
| flag_cont_mobile | int64 | 0.0 | Was mobile phone reachable (1=YES, 0=NO) |
| flag_phone | int64 | 0.0 | Did client provide home phone (1=YES, 0=NO) |
| flag_email | int64 | 0.0 | Did client provide email (1=YES, 0=NO) |
| occupation_type | str | 31.346 | What kind of occupation does the client have |
| cnt_fam_members | float64 | 0.001 | How many family members does client have |
| region_rating_client | int64 | 0.0 | Our rating of the region where client lives (1,2,3) |
| region_rating_client_w_city | int64 | 0.0 | Our rating of the region where client lives with taking city into account (1,2,3) |
| weekday_appr_process_start | str | 0.0 | On which day of the week did the client apply for the loan |
| hour_appr_process_start | int64 | 0.0 | Approximately at what hour did the client apply for the loan |
| reg_region_not_live_region | int64 | 0.0 | Flag if client's permanent address does not match contact address (1=different, 0=same, at region level) |
| reg_region_not_work_region | int64 | 0.0 | Flag if client's permanent address does not match work address (1=different, 0=same, at region level) |
| live_region_not_work_region | int64 | 0.0 | Flag if client's contact address does not match work address (1=different, 0=same, at region level) |
| reg_city_not_live_city | int64 | 0.0 | Flag if client's permanent address does not match contact address (1=different, 0=same, at city level) |
| reg_city_not_work_city | int64 | 0.0 | Flag if client's permanent address does not match work address (1=different, 0=same, at city level) |
| live_city_not_work_city | int64 | 0.0 | Flag if client's contact address does not match work address (1=different, 0=same, at city level) |
| organization_type | str | 18.007 | Type of organization where client works |
| ext_source_1 | float64 | 56.381 | Normalized score from external data source |
| ext_source_2 | float64 | 0.215 | Normalized score from external data source |
| ext_source_3 | float64 | 19.825 | Normalized score from external data source |
| apartments_avg | float64 | 50.75 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| basementarea_avg | float64 | 58.516 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| years_beginexpluatation_avg | float64 | 48.781 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| years_build_avg | float64 | 66.498 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| commonarea_avg | float64 | 69.872 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| elevators_avg | float64 | 53.296 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| entrances_avg | float64 | 50.349 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| floorsmax_avg | float64 | 49.761 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| floorsmin_avg | float64 | 67.849 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| landarea_avg | float64 | 59.377 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| livingapartments_avg | float64 | 68.355 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| livingarea_avg | float64 | 50.193 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| nonlivingapartments_avg | float64 | 69.433 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| nonlivingarea_avg | float64 | 55.179 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| apartments_mode | float64 | 50.75 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| basementarea_mode | float64 | 58.516 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| years_beginexpluatation_mode | float64 | 48.781 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| years_build_mode | float64 | 66.498 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| commonarea_mode | float64 | 69.872 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| elevators_mode | float64 | 53.296 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| entrances_mode | float64 | 50.349 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| floorsmax_mode | float64 | 49.761 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| floorsmin_mode | float64 | 67.849 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| landarea_mode | float64 | 59.377 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| livingapartments_mode | float64 | 68.355 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| livingarea_mode | float64 | 50.193 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| nonlivingapartments_mode | float64 | 69.433 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| nonlivingarea_mode | float64 | 55.179 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| apartments_medi | float64 | 50.75 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| basementarea_medi | float64 | 58.516 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| years_beginexpluatation_medi | float64 | 48.781 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| years_build_medi | float64 | 66.498 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| commonarea_medi | float64 | 69.872 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| elevators_medi | float64 | 53.296 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| entrances_medi | float64 | 50.349 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| floorsmax_medi | float64 | 49.761 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| floorsmin_medi | float64 | 67.849 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| landarea_medi | float64 | 59.377 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| livingapartments_medi | float64 | 68.355 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| livingarea_medi | float64 | 50.193 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| nonlivingapartments_medi | float64 | 69.433 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| nonlivingarea_medi | float64 | 55.179 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| fondkapremont_mode | str | 68.386 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| housetype_mode | str | 50.176 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| totalarea_mode | float64 | 48.269 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| wallsmaterial_mode | str | 50.841 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| emergencystate_mode | str | 47.398 | Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor |
| obs_30_cnt_social_circle | float64 | 0.332 | How many observation of client's social surroundings with observable 30 DPD (days past due) default |
| def_30_cnt_social_circle | float64 | 0.332 | How many observation of client's social surroundings defaulted on 30 DPD (days past due) |
| obs_60_cnt_social_circle | float64 | 0.332 | How many observation of client's social surroundings with observable 60 DPD (days past due) default |
| def_60_cnt_social_circle | float64 | 0.332 | How many observation of client's social surroundings defaulted on 60 (days past due) DPD |
| days_last_phone_change | float64 | 0.0 | How many days before application did client change phone |
| flag_document_2 | int64 | 0.0 | Did client provide document 2 |
| flag_document_3 | int64 | 0.0 | Did client provide document 3 |
| flag_document_4 | int64 | 0.0 | Did client provide document 4 |
| flag_document_5 | int64 | 0.0 | Did client provide document 5 |
| flag_document_6 | int64 | 0.0 | Did client provide document 6 |
| flag_document_7 | int64 | 0.0 | Did client provide document 7 |
| flag_document_8 | int64 | 0.0 | Did client provide document 8 |
| flag_document_9 | int64 | 0.0 | Did client provide document 9 |
| flag_document_10 | int64 | 0.0 | Did client provide document 10 |
| flag_document_11 | int64 | 0.0 | Did client provide document 11 |
| flag_document_12 | int64 | 0.0 | Did client provide document 12 |
| flag_document_13 | int64 | 0.0 | Did client provide document 13 |
| flag_document_14 | int64 | 0.0 | Did client provide document 14 |
| flag_document_15 | int64 | 0.0 | Did client provide document 15 |
| flag_document_16 | int64 | 0.0 | Did client provide document 16 |
| flag_document_17 | int64 | 0.0 | Did client provide document 17 |
| flag_document_18 | int64 | 0.0 | Did client provide document 18 |
| flag_document_19 | int64 | 0.0 | Did client provide document 19 |
| flag_document_20 | int64 | 0.0 | Did client provide document 20 |
| flag_document_21 | int64 | 0.0 | Did client provide document 21 |
| amt_req_credit_bureau_hour | float64 | 13.502 | Number of enquiries to Credit Bureau about the client one hour before application |
| amt_req_credit_bureau_day | float64 | 13.502 | Number of enquiries to Credit Bureau about the client one day before application (excluding one hour before application) |
| amt_req_credit_bureau_week | float64 | 13.502 | Number of enquiries to Credit Bureau about the client one week before application (excluding one day before application) |
| amt_req_credit_bureau_mon | float64 | 13.502 | Number of enquiries to Credit Bureau about the client one month before application (excluding one week before application) |
| amt_req_credit_bureau_qrt | float64 | 13.502 | Number of enquiries to Credit Bureau about the client 3 month before application (excluding one month before application) |
| amt_req_credit_bureau_year | float64 | 13.502 | Number of enquiries to Credit Bureau about the client one day year (excluding last 3 months before application) |
| days_employed_is_anomalous | int8 | 0.0 | bayraq: DAYS_EMPLOYED=365243 sentineli idi |

## Aqreqat sütunlar (SK_ID_CURR səviyyəsi)
| sütun | dtype | null % | mənbə cədvəl | mənbə sütun | stat |
|---|---|---|---|---|---|
| bureau_sk_id_bureau_count | int32 | 0.0 | bureau | SK_ID_BUREAU | count |
| bureau_active_sum | float64 | 14.315 | bureau | CREDIT_ACTIVE | sum |
| bureau_active_mean | float64 | 14.315 | bureau | CREDIT_ACTIVE | mean |
| bureau_closed_sum | float64 | 14.315 | bureau | CREDIT_ACTIVE | sum |
| bureau_has_overdue_sum | float64 | 14.315 | bureau | CREDIT_DAY_OVERDUE | sum |
| bureau_days_credit_min | float64 | 14.315 | bureau | DAYS_CREDIT | min |
| bureau_days_credit_max | float64 | 14.315 | bureau | DAYS_CREDIT | max |
| bureau_days_credit_mean | float64 | 14.315 | bureau | DAYS_CREDIT | mean |
| bureau_credit_day_overdue_max | float64 | 14.315 | bureau | CREDIT_DAY_OVERDUE | max |
| bureau_credit_day_overdue_mean | float64 | 14.315 | bureau | CREDIT_DAY_OVERDUE | mean |
| bureau_days_credit_enddate_min | float64 | 15.046 | bureau | DAYS_CREDIT_ENDDATE | min |
| bureau_days_credit_enddate_max | float64 | 15.046 | bureau | DAYS_CREDIT_ENDDATE | max |
| bureau_amt_credit_max_overdue_max | float64 | 40.202 | bureau | AMT_CREDIT_MAX_OVERDUE | max |
| bureau_cnt_credit_prolong_sum | float64 | 14.315 | bureau | CNT_CREDIT_PROLONG | sum |
| bureau_cnt_credit_prolong_max | float64 | 14.315 | bureau | CNT_CREDIT_PROLONG | max |
| bureau_amt_credit_sum_sum | float64 | 14.315 | bureau | AMT_CREDIT_SUM | sum |
| bureau_amt_credit_sum_mean | float64 | 14.315 | bureau | AMT_CREDIT_SUM | mean |
| bureau_amt_credit_sum_max | float64 | 14.315 | bureau | AMT_CREDIT_SUM | max |
| bureau_amt_credit_sum_debt_sum | float64 | 16.708 | bureau | AMT_CREDIT_SUM_DEBT | sum |
| bureau_amt_credit_sum_debt_max | float64 | 16.708 | bureau | AMT_CREDIT_SUM_DEBT | max |
| bureau_amt_credit_sum_limit_sum | float64 | 21.16 | bureau | AMT_CREDIT_SUM_LIMIT | sum |
| bureau_amt_credit_sum_overdue_sum | float64 | 14.315 | bureau | AMT_CREDIT_SUM_OVERDUE | sum |
| bureau_amt_credit_sum_overdue_max | float64 | 14.315 | bureau | AMT_CREDIT_SUM_OVERDUE | max |
| bureau_amt_annuity_sum | float64 | 73.982 | bureau | AMT_ANNUITY | sum |
| bureau_amt_annuity_mean | float64 | 73.982 | bureau | AMT_ANNUITY | mean |
| bureau_has_bb_sum | float64 | 14.315 | bureau_balance | SK_ID_BUREAU | sum |
| bureau_months_count_sum | float64 | 70.007 | bureau_balance | MONTHS_BALANCE | sum |
| bureau_months_count_max | float64 | 70.007 | bureau_balance | MONTHS_BALANCE | max |
| bureau_months_oldest_max | float64 | 70.007 | bureau_balance | MONTHS_BALANCE | max |
| bureau_dpd_months_sum | float64 | 70.007 | bureau_balance | STATUS | sum |
| bureau_dpd_months_max | float64 | 70.007 | bureau_balance | STATUS | max |
| bureau_dpd_severe_months_sum | float64 | 70.007 | bureau_balance | STATUS | sum |
| bureau_dpd_share_mean | float64 | 70.007 | bureau_balance | STATUS | mean |
| bureau_dpd_share_max | float64 | 70.007 | bureau_balance | STATUS | max |
| bureau_credit_type_nunique | int32 | 0.0 | bureau | CREDIT_TYPE | nunique |
| bureau_has_history | int8 | 0.0 | bureau | SK_ID_CURR | has_history |
| previous_application_sk_id_prev_count | int32 | 0.0 | previous_application | SK_ID_PREV | count |
| previous_application_approved_sum | float64 | 5.351 | previous_application | NAME_CONTRACT_STATUS | sum |
| previous_application_approved_mean | float64 | 5.351 | previous_application | NAME_CONTRACT_STATUS | mean |
| previous_application_refused_sum | float64 | 5.351 | previous_application | NAME_CONTRACT_STATUS | sum |
| previous_application_refused_mean | float64 | 5.351 | previous_application | NAME_CONTRACT_STATUS | mean |
| previous_application_canceled_sum | float64 | 5.351 | previous_application | NAME_CONTRACT_STATUS | sum |
| previous_application_amt_application_mean | float64 | 5.351 | previous_application | AMT_APPLICATION | mean |
| previous_application_amt_application_max | float64 | 5.351 | previous_application | AMT_APPLICATION | max |
| previous_application_amt_application_sum | float64 | 5.351 | previous_application | AMT_APPLICATION | sum |
| previous_application_amt_credit_mean | float64 | 5.351 | previous_application | AMT_CREDIT | mean |
| previous_application_amt_credit_max | float64 | 5.351 | previous_application | AMT_CREDIT | max |
| previous_application_amt_credit_sum | float64 | 5.351 | previous_application | AMT_CREDIT | sum |
| previous_application_amt_annuity_mean | float64 | 5.486 | previous_application | AMT_ANNUITY | mean |
| previous_application_amt_annuity_max | float64 | 5.486 | previous_application | AMT_ANNUITY | max |
| previous_application_amt_down_payment_mean | float64 | 11.026 | previous_application | AMT_DOWN_PAYMENT | mean |
| previous_application_amt_down_payment_max | float64 | 11.026 | previous_application | AMT_DOWN_PAYMENT | max |
| previous_application_amt_goods_price_mean | float64 | 5.668 | previous_application | AMT_GOODS_PRICE | mean |
| previous_application_amt_goods_price_max | float64 | 5.668 | previous_application | AMT_GOODS_PRICE | max |
| previous_application_rate_down_payment_mean | float64 | 11.026 | previous_application | RATE_DOWN_PAYMENT | mean |
| previous_application_cnt_payment_mean | float64 | 5.486 | previous_application | CNT_PAYMENT | mean |
| previous_application_cnt_payment_max | float64 | 5.486 | previous_application | CNT_PAYMENT | max |
| previous_application_days_decision_min | float64 | 5.351 | previous_application | DAYS_DECISION | min |
| previous_application_days_decision_max | float64 | 5.351 | previous_application | DAYS_DECISION | max |
| previous_application_days_decision_mean | float64 | 5.351 | previous_application | DAYS_DECISION | mean |
| previous_application_has_history | int8 | 0.0 | previous_application | SK_ID_CURR | has_history |
| pos_cash_balance_sk_id_prev_count | int32 | 0.0 | POS_CASH_balance | SK_ID_PREV | count |
| pos_cash_balance_sk_id_prev_nunique | int32 | 0.0 | POS_CASH_balance | SK_ID_PREV | nunique |
| pos_cash_balance_months_balance_min | float64 | 5.875 | POS_CASH_balance | MONTHS_BALANCE | min |
| pos_cash_balance_months_balance_max | float64 | 5.875 | POS_CASH_balance | MONTHS_BALANCE | max |
| pos_cash_balance_cnt_instalment_mean | float64 | 5.883 | POS_CASH_balance | CNT_INSTALMENT | mean |
| pos_cash_balance_cnt_instalment_max | float64 | 5.883 | POS_CASH_balance | CNT_INSTALMENT | max |
| pos_cash_balance_cnt_instalment_future_mean | float64 | 5.883 | POS_CASH_balance | CNT_INSTALMENT_FUTURE | mean |
| pos_cash_balance_cnt_instalment_future_min | float64 | 5.883 | POS_CASH_balance | CNT_INSTALMENT_FUTURE | min |
| pos_cash_balance_sk_dpd_max | float64 | 5.875 | POS_CASH_balance | SK_DPD | max |
| pos_cash_balance_sk_dpd_mean | float64 | 5.875 | POS_CASH_balance | SK_DPD | mean |
| pos_cash_balance_sk_dpd_def_max | float64 | 5.875 | POS_CASH_balance | SK_DPD_DEF | max |
| pos_cash_balance_sk_dpd_def_mean | float64 | 5.875 | POS_CASH_balance | SK_DPD_DEF | mean |
| pos_cash_balance_completed_sum | float64 | 5.875 | POS_CASH_balance | NAME_CONTRACT_STATUS | sum |
| pos_cash_balance_has_history | int8 | 0.0 | POS_CASH_balance | SK_ID_CURR | has_history |
| credit_card_balance_sk_id_prev_count | int32 | 0.0 | credit_card_balance | SK_ID_PREV | count |
| credit_card_balance_sk_id_prev_nunique | int32 | 0.0 | credit_card_balance | SK_ID_PREV | nunique |
| credit_card_balance_months_balance_min | float64 | 71.739 | credit_card_balance | MONTHS_BALANCE | min |
| credit_card_balance_amt_balance_mean | float64 | 71.739 | credit_card_balance | AMT_BALANCE | mean |
| credit_card_balance_amt_balance_max | float64 | 71.739 | credit_card_balance | AMT_BALANCE | max |
| credit_card_balance_amt_credit_limit_actual_mean | float64 | 71.739 | credit_card_balance | AMT_CREDIT_LIMIT_ACTUAL | mean |
| credit_card_balance_amt_credit_limit_actual_max | float64 | 71.739 | credit_card_balance | AMT_CREDIT_LIMIT_ACTUAL | max |
| credit_card_balance_amt_drawings_current_sum | float64 | 71.739 | credit_card_balance | AMT_DRAWINGS_CURRENT | sum |
| credit_card_balance_amt_drawings_current_mean | float64 | 71.739 | credit_card_balance | AMT_DRAWINGS_CURRENT | mean |
| credit_card_balance_amt_payment_current_sum | float64 | 80.144 | credit_card_balance | AMT_PAYMENT_CURRENT | sum |
| credit_card_balance_amt_payment_current_mean | float64 | 80.144 | credit_card_balance | AMT_PAYMENT_CURRENT | mean |
| credit_card_balance_amt_receivable_principal_mean | float64 | 71.739 | credit_card_balance | AMT_RECEIVABLE_PRINCIPAL | mean |
| credit_card_balance_amt_receivable_principal_max | float64 | 71.739 | credit_card_balance | AMT_RECEIVABLE_PRINCIPAL | max |
| credit_card_balance_sk_dpd_max | float64 | 71.739 | credit_card_balance | SK_DPD | max |
| credit_card_balance_sk_dpd_mean | float64 | 71.739 | credit_card_balance | SK_DPD | mean |
| credit_card_balance_sk_dpd_def_max | float64 | 71.739 | credit_card_balance | SK_DPD_DEF | max |
| credit_card_balance_sk_dpd_def_mean | float64 | 71.739 | credit_card_balance | SK_DPD_DEF | mean |
| credit_card_balance_has_history | int8 | 0.0 | credit_card_balance | SK_ID_CURR | has_history |
| installments_payments_sk_id_prev_count | int32 | 0.0 | installments_payments | SK_ID_PREV | count |
| installments_payments_sk_id_prev_nunique | int32 | 0.0 | installments_payments | SK_ID_PREV | nunique |
| installments_payments_num_instalment_number_max | float64 | 5.16 | installments_payments | NUM_INSTALMENT_NUMBER | max |
| installments_payments_amt_instalment_sum | float64 | 5.16 | installments_payments | AMT_INSTALMENT | sum |
| installments_payments_amt_instalment_mean | float64 | 5.16 | installments_payments | AMT_INSTALMENT | mean |
| installments_payments_amt_instalment_max | float64 | 5.16 | installments_payments | AMT_INSTALMENT | max |
| installments_payments_amt_payment_sum | float64 | 5.163 | installments_payments | AMT_PAYMENT | sum |
| installments_payments_amt_payment_mean | float64 | 5.163 | installments_payments | AMT_PAYMENT | mean |
| installments_payments_days_late_max | float64 | 5.163 | installments_payments | DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT | max |
| installments_payments_days_late_mean | float64 | 5.163 | installments_payments | DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT | mean |
| installments_payments_is_late_sum | float64 | 5.16 | installments_payments | DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT | sum |
| installments_payments_is_late_mean | float64 | 5.16 | installments_payments | DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT | mean |
| installments_payments_amt_unpaid_sum | float64 | 5.163 | installments_payments | AMT_INSTALMENT-AMT_PAYMENT | sum |
| installments_payments_amt_unpaid_max | float64 | 5.163 | installments_payments | AMT_INSTALMENT-AMT_PAYMENT | max |
| installments_payments_has_history | int8 | 0.0 | installments_payments | SK_ID_CURR | has_history |
