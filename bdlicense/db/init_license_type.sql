-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (1,'1','基础功能');
-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (2,'2','计费功能');
-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (3,'3','地图功能');
-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (3,'4','大数据分析功能');

INSERT INTO auth_user(username, password,is_staff,is_active,is_superuser,user_level) VALUES ('root', 'pbkdf2_sha256$20000$VLpgVrkzqlIA$xD0KuNxejkse6lLac4pync5covu1WLLWx2LZpHQ27to=',1,1,1,1);
INSERT INTO auth_user(username, password,is_staff,is_active,is_superuser,user_level) VALUES ('bdyun', 'pbkdf2_sha256$20000$VLpgVrkzqlIA$xD0KuNxejkse6lLac4pync5covu1WLLWx2LZpHQ27to=',1,1,0,0);
INSERT INTO auth_user(username, password,is_staff,is_active,is_superuser,user_level) VALUES ('license', 'pbkdf2_sha256$20000$VLpgVrkzqlIA$xD0KuNxejkse6lLac4pync5covu1WLLWx2LZpHQ27to=',1,1,0,2);

INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (1,'CBSOF-CDS0047A','BCP8200-OS-STD',4,0,0,1,1);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (2,'CBSOF-CDS0052A','BCP8200-Lic-64',64,1,1280,1,2);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (3,'CBSOF-CDS0053A','BCP8200-Lic-128',128,2,2560,1,2);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (4,'CBSOF-CDS0055A','BCP8200-Lic-1024',1024,4,20480,1,2);

INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (5,'CBSOF-CDS0095A','BCP8200-Ext-Map-0',8,0,0,1,3);

INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (6,'ZXSOF-CDS0004A','ZXWL OMCP',4,0,0,2,1);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (7,'ZXSOF-CDS0017A','ZXWL OMCP（精简版）',1,0,0,2,1);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (8,'ZXSOF-CDS0014A','ZXWL OMCP-License',1024,4,20480,2,2);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (9,'ZXSOF-CDS0015A','ZXWL OMCP-License',32,1,640,2,2);
INSERT INTO adminbd_licenseparams(id,code,cloudRankName,maxAPs,maxACs,maxUsers,vesion_type,product_type) VALUES (10,'ZXSOF-CDS0016A','ZXWL OMCP-License',128,2,2560,2,2);
