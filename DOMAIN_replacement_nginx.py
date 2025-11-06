MDH DOMAIN REPLACEMENT IN NGINX |
================================

1 certificate holds 5 domains for free.
OVERALL CODE
-------------
		sudo add-apt-repository ppa:certbot/certbot -y && sudo apt-get update -y
	  	sudo apt-get install python3-certbot-nginx -y
	  	sudo certbot --nginx -d $WEBSITE_NAME --noninteractive --agree-tos --email $ADMIN_EMAIL --redirect
	  	sudo service nginx reload
		sudo certbot --nginx -d hom.marvelsa.com

		sudo certbot --nginx -d portal.arrendadoramarvelsa.com -d https://www.portal.arrendadoramarvelsa.com -d transportesmarvelsa.com -d https://www.transportesmarvelsa.com --expand --noninteractive --agree-tos --email mailto:kishan@setuconsulting.com --redirect
		sudo certbot --nginx -d testing16.agrobolder.com -d tod16.agrobolder.com --expand --noninteractive --agree-tos --email mailto:vivek@setuconsulting.com --redirect  
		sudo certbot --nginx -d portal.agrobolder.com



DOMAIN REPLACE
--------------
REQUIREMENT : Remove the subdomain "tod16.mdhbikes.com" from Nginx and replace it with "tod16.mdhsports.com"
	      Remove the subdomain "hom.mdhbikes.com" from Nginx 
	      
SOLUTION : Remove the subdomain "tod16.mdhbikes.com" from Nginx and replace it with "tod16.mdhsports.com"
========================================================================================================
	First login in terminal : 
       ------------------------	
				 ssh -i /home/setu20/.ssh/odoo_16 odoo16@tod16.mdhbikes.com
				 
				 odoo16@us1alx010:~$ cd /etc/nginx	      
				 		      ls
				 		      cd /etc/nginx/sites-enabled/
				
				Enter the file : odoo_ng.conf by giving the sudo. 
						 sudo is given to get all the permission. 
						 If sudo is not given than also it will allow to enter the file but while saving the file it will ask for permission.
						 
   	 		        odoo16@us1alx010:/etc/nginx/sites-enabled$ sudo vim odoo_ng.conf / sudo vi odoo_ng.conf

   	 		        (Things to be changed in file)
   	 		        
   	 		        server {
   	 		        		
					  server_name tod16.mdhbikes.com; 
				
   	 		        
				    listen 443 ssl; # managed by Certbot
				    ssl_certificate /etc/letsencrypt/live/tod16.mdhbikes.com/fullchain.pem; # managed by Certbot
				    ssl_certificate_key /etc/letsencrypt/live/tod16.mdhbikes.com/privkey.pem; # managed by Certbot
				    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
				    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
						
				server {
					    if ($host = tod16.mdhbikes.com) {
					        return 301 https://$host$request_uri;
					    } # managed by Certbot
					  listen 80 ;
					  server_name tod16.mdhbikes.com;
					    return 404; # managed by Certbot
					}

	CHANGES TO BE DONE in FILE :
       ----------------------------
       		 server {
   	 		        		
					  server_name tod16.mdhsports.com
					   
			COMMENT THE BELOW CODE by giving # and write after the commented code:
	   		            #listen 443 ssl; # managed by Certbot
				    #ssl_certificate /etc/letsencrypt/live/tod16.mdhbikes.com/fullchain.pem; # managed by Certbot
				    #ssl_certificate_key /etc/letsencrypt/live/tod16.mdhbikes.com/privkey.pem; # managed by Certbot
				    #include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
				    #ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
	    			    
				    listen 80
				}
				
			COMMENT THE BELOW CODE : 
			
				#server {
				#    if ($host = tod16.mdhbikes.com) {
				#        return 301 https://$host$request_uri;
				#    } # managed by Certbot
				#  listen 80 ;
				#  server_name tod16.mdhbikes.com;
				#    return 404; # managed by Certbot


				#}
			SAVE THE FILE : esc :wq
			Again enter the file to see the changes: Certbot will directly create a certificate for tod16.mdhsports.com
			odoo16@us1alx010:/etc/nginx/sites-enabled$ sudo vi odoo_ng.conf

			Changes will be as mentioned below :
			----------------------------------
				server {
					  server_name tod16.mdhsports.com;	
						# other code						
		
					    listen 443 ssl; # managed by Certbot
					    ssl_certificate /etc/letsencrypt/live/tod16.mdhsports.com/fullchain.pem; # managed by Certbot
					    ssl_certificate_key /etc/letsencrypt/live/tod16.mdhsports.com/privkey.pem; # managed by Certbot
					    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
					    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

					}
					server {
						    if ($host = tod16.mdhsports.com) {
							return 301 https://$host$request_uri;
						    } # managed by Certbot


						  server_name tod16.mdhsports.com;
						    listen 80;
						    return 404; # managed by Certbot
						}


				
			
			odoo16@us1alx010:/etc/nginx/sites-enabled$ sudo killall python3.8
								     sudo service nginx stop
								     sudo service nginx restart
								     (if any error is occured stop all the odoo process and restart the process)
								     ps aux | grep odoo
								     sudo service nginx restart
								     sudo service odoo16-server restart

	REMOVE THE DOMAIN FROM OTHER FILE:
	----------------------------------
		odoo16@us1alx010: sudo ls /etc/letsencrypt/live/								     
				  (will give) README  tod16.mdhbikes.com tod16.mdhsports.com
				  sudo su root
				  rm -rf hom.mdhbikes.com 
				  rm -rf tod16.mdhbikes.com 
								     
-------------------------------------------------------------------------------------------------------------------------------------------------------
				    
SOLUTION : Remove the subdomain "hom.mdhbikes.com" from Nginx 
=============================================================				    
	First login in terminal : 
       ------------------------	
				 ssh -i /home/setu20/.ssh/odoo_16 odoo16@tod16.mdhbikes.com
				 
				 odoo16@us1alx010:~$ cd /etc/nginx	      
				 		      ls
				 		      cd /etc/nginx/sites-enabled/
				
				Enter the file : odoo_hgm by giving the sudo. 
						   sudo vim odoo_hgm
						   
				(Things to be changed in file: Direct changes are given here)
				-------------------------------------------------------------
					server {
						  server_name _; (write _(underscore) to blank the domain
						  
					  gzip on; (comment the below part and write listen 80 after gzip on)

					#    listen 443 ssl; # managed by Certbot
					#    ssl_certificate /etc/letsencrypt/live/hom.mdhbikes.com/fullchain.pem; # managed by Certbot
					#    ssl_certificate_key /etc/letsencrypt/live/hom.mdhbikes.com/privkey.pem; # managed by Certbot
					#    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
					#    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
					     listen 80;
					}
					(Comment below part too)
					#server {
					#    if ($host = hom.mdhbikes.com) {
					#        return 301 https://$host$request_uri;
					#    } # managed by Certbot


					#  server_name hom.mdhbikes.com;

					#listen 80;
					#    return 404; # managed by Certbot


					#}
			SAVE THE FILE : esc :wq
			odoo16@us1alx010:/etc/nginx/sites-enabled$   sudo service nginx stop		
		
	REMOVE THE DOMAIN FROM OTHER FILE:
	----------------------------------
		odoo16@us1alx010: sudo ls /etc/letsencrypt/live/								     
				  (will give) README hom.mdhbikes.com  tod16.mdhbikes.com tod16.mdhsports.com
				  sudo su root
				  rm -rf hom.mdhbikes.com 
								


	  
						  
						  
						  
				

