INSERT INTO adminbd_licensetype (id,type,discription) VALUES (1,'1','基础功能');
INSERT INTO adminbd_licensetype (id,type,discription) VALUES (2,'2','计费功能');
INSERT INTO adminbd_licensetype (id,type,discription) VALUES (3,'3','地图功能');
INSERT INTO adminbd_licensetype (id,type,discription) VALUES (4,'4','大数据分析功能');



INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (1,'低配',128,128,999);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (2,'中配',256,25,9999);
INSERT INTO adminbd_licenseparams(id,cloudRankName,maxAPs,maxACs,maxUsers) VALUES (3,'高配',1024,1024,99999);