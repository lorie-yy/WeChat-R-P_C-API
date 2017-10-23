-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (1,'1','基础功能');
-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (2,'2','计费功能');
-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (3,'3','地图功能');
-- INSERT INTO adminbd_licensetype (id,type,discription) VALUES (3,'4','大数据分析功能');

INSERT INTO auth_user(username, password,is_staff,is_active,is_superuser,user_level) VALUES ('root', 'pbkdf2_sha256$20000$VLpgVrkzqlIA$xD0KuNxejkse6lLac4pync5covu1WLLWx2LZpHQ27to=',1,1,1,1);
INSERT INTO auth_user(username, password,is_staff,is_active,is_superuser,user_level) VALUES ('bdyun', 'pbkdf2_sha256$20000$VLpgVrkzqlIA$xD0KuNxejkse6lLac4pync5covu1WLLWx2LZpHQ27to=',1,1,0,0);
INSERT INTO auth_user(username, password,is_staff,is_active,is_superuser,user_level) VALUES ('license', 'pbkdf2_sha256$20000$VLpgVrkzqlIA$xD0KuNxejkse6lLac4pync5covu1WLLWx2LZpHQ27to=',1,1,0,2);

INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (1,'BCP8200-Lic-32',32,1,640);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (2,'BCP8200-Lic-64',64,1,1280);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (3,'BCP8200-Lic-128',128,1,2560);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (4,'BCP8200-Lic-512',512,2,10240);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (5,'BCP8200-Lic-1024',1024,4,20480);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (6,'测试版--16X1X32',16,1,32);