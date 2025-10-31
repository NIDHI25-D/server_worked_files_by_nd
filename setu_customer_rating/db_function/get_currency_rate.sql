CREATE OR REPLACE FUNCTION public.get_nearest_currency_rate(
    IN date_name date,
    IN company integer
)
  RETURNS TABLE(currency_id integer, name character varying, rate numeric) AS

$BODY$
BEGIN

        Return Query

select rc.id as currency_id,rc.name,rates.rate from res_currency rc
inner join
	(select rcr.currency_id,rcr.name,rcr.rate from res_currency_rate rcr
	 	inner join
	 	(select rcr2.currency_id,max(rcr2.name)as name from res_currency_rate rcr2 where rcr2.name <= date_name and rcr2.company_id = company group by rcr2.currency_id)as max_rate
	 	on rcr.currency_id = max_rate.currency_id and rcr.name = max_rate.name
	)as rates on rates.currency_id = rc.id;


END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
