# -*- coding: utf-8 -*-

##
# Copyright (с) Ildar Bikmamatov 2022
# License: MIT
##

import os, time, torch, json
from torch.utils.data import TensorDataset, DataLoader, Dataset
from .utils import get_tensor_device, list_files, indexOf, get_class_name


class TrainHistory:
	
	def __init__(self):
		
		self.epoch_number = 0
		self.epoch = {}
	
	
	def clear(self):
		
		"""
		Clear history
		"""
		
		self.epoch_number = 0
		self.epoch = {}
	
	
	def load_state_dict(self, dict):
		
		"""
		Load state
		"""
		
		self.epoch_number = dict["epoch_number"]
		self.epoch = dict["epoch"]
	
	
	def state_dict(self):
		
		"""
		Get state
		"""
		
		obj = {
			"epoch_number": self.epoch_number,
			"epoch": self.epoch,
		}
		
		return obj
	
	
	def add(self, record):
		
		"""
		Add train history from record
		"""
		
		epoch_number = record["epoch_number"]
		self.epoch_number = epoch_number
		self.epoch[epoch_number] = {
			
			"loss_train": record["loss_train"],
			"loss_val": record["loss_val"],
			"acc_train": record["acc_train"],
			"acc_val": record["acc_val"],
			"acc_rel": record["acc_rel"],
			"time": record["time"],
			"lr": record["lr"],
			"batch_train_iter": record["batch_train_iter"],
			"batch_val_iter": record["batch_val_iter"],
			"count_train_iter": record["count_train_iter"],
			"count_val_iter": record["count_val_iter"],
			"loss_train_iter": record["loss_train_iter"],
			"loss_val_iter": record["loss_val_iter"],
			"acc_train_iter": record["acc_train_iter"],
			"acc_val_iter": record["acc_val_iter"],
			
		}
	
	
	def add_train_status(self, train_status):
		
		"""
		Add train history from train status
		"""
		
		loss_train = train_status.get_loss_train()
		loss_val = train_status.get_loss_val()
		acc_train = train_status.get_acc_train()
		acc_val = train_status.get_acc_val()
		acc_rel = train_status.get_acc_rel()
		time = train_status.get_time()
		lr = train_status.get_lr()
		
		self.add( {
			
			"epoch_number": train_status.epoch_number,
			"loss_train": loss_train,
			"loss_val": loss_val,
			"acc_train": acc_train,
			"acc_val": acc_val,
			"acc_rel": acc_rel,
			"time": time,
			"lr": json.dumps(lr),
			"batch_train_iter": train_status.batch_train_iter,
			"batch_val_iter": train_status.batch_val_iter,
			"count_train_iter": train_status.count_train_iter,
			"count_val_iter": train_status.count_val_iter,
			"loss_train_iter": train_status.loss_train_iter,
			"loss_val_iter": train_status.loss_val_iter,
			"acc_train_iter": train_status.acc_train_iter,
			"acc_val_iter": train_status.acc_val_iter,
			
		} )
	
	
	def get_epoch(self, epoch_number):
		
		"""
		Returns epoch by number
		"""
		
		if not(epoch_number in self.epoch):
			return None
			
		return self.epoch[epoch_number]
	
	
	def get_metrics(self, metric_name, with_index=False):
		
		"""
		Returns metrics by name
		"""
		
		res = []
		for index in self.epoch:
			
			epoch = self.get_epoch(index)
			
			if with_index:
				if isinstance(metric_name, list):
					res2 = [ index ]
					for name in metric_name:
						res2.append( epoch[name] if name in epoch else 0 )
					res.append( tuple(res2) )
				else:
					res.append( (index, epoch[metric_name] if metric_name in epoch else 0) )
			else:
				res.append( epoch[metric_name] if metric_name in epoch else 0 )
		
		return res
	
	
	def plot(self, ax, kind=""):
		
		"""
		Returns train history
		"""
		
		import numpy as np
		
		if kind == "loss":
			loss_train = self.get_metrics("loss_train")
			loss_val = self.get_metrics("loss_val")
			
			ax.plot( np.multiply(loss_train, 100), label='loss_train')
			ax.plot( np.multiply(loss_val, 100), label='loss_val')
			ax.legend()
		
		if kind == "acc":
			acc_train = self.get_metrics("acc_train")
			acc_val = self.get_metrics("acc_val")
			
			ax.plot( np.multiply(acc_train, 100), label='acc_train')
			ax.plot( np.multiply(acc_val, 100), label='acc_val')
			ax.legend()
		
	

class TrainStatus:
	
	def __init__(self):
		self.model = None
		self.batch_size = 0
		self.batch_train_iter = 0
		self.batch_val_iter = 0
		self.count_train_iter = 0
		self.count_val_iter = 0
		self.loss_train_iter = 0
		self.loss_val_iter = 0
		self.acc_train_iter = 0
		self.acc_val_iter = 0
		self.epoch_number = 0
		self.trainer = None
		self.do_training = True
		self.train_data_count = 0
		self.time_start = 0
		self.time_end = 0
	
	def set_model(self, model):
		
		self.clear()
		self.model = model
		self.epoch_number = model._history.epoch_number
		
		if self.epoch_number > 0:
			
			record = model._history.get_epoch(self.epoch_number)
			
			self.batch_train_iter = record["batch_train_iter"] if "batch_train_iter" in record else 0
			self.batch_val_iter = record["batch_val_iter"] if "batch_val_iter" in record else 0
			self.count_train_iter = record["count_train_iter"] if "count_train_iter" in record else 0
			self.count_val_iter = record["count_val_iter"] if "count_val_iter" in record else 0
			self.loss_train_iter = record["loss_train_iter"] if "loss_train_iter" in record else 0
			self.loss_val_iter = record["loss_val_iter"] if "loss_val_iter" in record else 0
			self.acc_train_iter = record["acc_train_iter"] if "acc_train_iter" in record else 0
			self.acc_val_iter = record["acc_val_iter"] if "acc_val_iter" in record else 0
	
	def clear(self):
		self.clear_iter()
	
	def clear_iter(self):
		self.batch_train_iter = 0
		self.batch_val_iter = 0
		self.count_train_iter = 0
		self.count_val_iter = 0
		self.loss_train_iter = 0
		self.loss_val_iter = 0
		self.acc_train_iter = 0
		self.acc_val_iter = 0
	
	def get_iter_value(self):
		if self.train_data_count == 0:
			return 0
		return (self.count_train_iter + self.count_val_iter) / self.train_data_count
	
	def get_loss_train(self):
		if self.batch_train_iter == 0:
			return 0
		return self.loss_train_iter / self.batch_train_iter
	
	def get_loss_val(self):
		if self.batch_val_iter == 0:
			return 0
		return self.loss_val_iter / self.batch_val_iter
	
	def get_acc_train(self):
		if self.count_train_iter == 0:
			return 0
		return self.acc_train_iter / self.count_train_iter
	
	def get_acc_val(self):
		if self.count_val_iter == 0:
			return 0
		return self.acc_val_iter / self.count_val_iter
	
	def get_acc_rel(self):
		acc_train = self.get_acc_train()
		acc_val = self.get_acc_val()
		if acc_val == 0:
			return 0
		return acc_train / acc_val
	
	def get_loss_rel(self):
		if self.loss_val == 0:
			return 0
		return self.loss_train / self.loss_val
	
	def stop_train(self):
		self.do_training = False
	
	def get_time(self):
		return self.time_end - self.time_start
	
	def get_lr(self):
		
		res_lr = []
		for param_group in self.trainer.optimizer.param_groups:
			res_lr.append(param_group['lr'])
			
		return res_lr


class TrainAccuracyCallback:
	
	def get_acc(self, batch_y, batch_predict):
		
		batch_y = torch.argmax(batch_y, dim=1)
		batch_predict = torch.argmax(batch_predict, dim=1)
		acc = torch.sum( torch.eq(batch_y, batch_predict) ).item()
		
		return acc
	
	
	def on_end_batch_train(self, trainer, batch_x, batch_y, batch_predict, loss):
		
		acc = self.get_acc(batch_y, batch_predict)
		trainer.train_status.acc_train_iter = trainer.train_status.acc_train_iter + acc
	
	
	def on_end_batch_test(self, trainer, batch_x, batch_y, batch_predict, loss):
		
		acc = self.get_acc(batch_y, batch_predict)
		trainer.train_status.acc_val_iter = trainer.train_status.acc_val_iter + acc
	

class TrainVerboseCallback:
	
	def print_train(self, trainer, batch_x, batch_y, batch_predict, loss):
		
		acc_train = trainer.train_status.get_acc_train()
		loss_train = trainer.train_status.get_loss_train()
		time = trainer.train_status.get_time()
		
		loss_train = '%.3e' % loss_train
		
		msg = ("\rStep {epoch_number}, {iter_value}%" +
			", acc: {acc}, loss: {loss}, time: {time}s"
		).format(
			epoch_number = trainer.train_status.epoch_number,
			iter_value = round(trainer.train_status.get_iter_value() * 100),
			loss = loss_train,
			acc = str(round(acc_train * 100) / 100).ljust(4, "0"),
			time = str(round(time)),
		)
		
		print (msg, end='')
		
	
	def on_end_batch_test(self, trainer, batch_x, batch_y, batch_predict, loss):
		
		self.print_train(trainer, batch_x, batch_y, batch_predict, loss)
	
	
	def on_end_batch_train(self, trainer, batch_x, batch_y, batch_predict, loss):
		
		self.print_train(trainer, batch_x, batch_y, batch_predict, loss)
	
	
	def on_end_epoch(self, trainer):
		
		"""
		Epoch
		"""
		
		loss_train = trainer.train_status.get_loss_train()
		loss_val = trainer.train_status.get_loss_val()
		acc_train = trainer.train_status.get_acc_train()
		acc_val = trainer.train_status.get_acc_val()
		acc_rel = trainer.train_status.get_acc_rel()
		time = trainer.train_status.get_time()
		res_lr = trainer.train_status.get_lr()
		
		loss_train = '%.3e' % loss_train
		loss_val = '%.3e' % loss_val
		
		print ("\r", end='')
		
		msg = ("Step {epoch_number}, " +
			"acc: {acc_train}, " +
			"acc_val: {acc_val}, " +
			"acc_rel: {acc_rel}, " +
			"loss: {loss_train}, " +
			"loss_val: {loss_val}, " +
			"lr: {lr}, " +
			"time: {time}s "
		).format(
			epoch_number = trainer.train_status.epoch_number,
			loss_train = loss_train,
			loss_val = loss_val,
			acc_train = str(round(acc_train * 10000) / 10000).ljust(6, "0"),
			acc_val = str(round(acc_val * 10000) / 10000).ljust(6, "0"),
			acc_rel = str(round(acc_rel * 10000) / 10000).ljust(6, "0"),
			time = str(round(time)),
			lr = str(res_lr),
		)
		
		print (msg)
	

class TrainShedulerCallback:
	
	def __init__(self):
		self.scheduler = None
	
	
	def save_metrics(self, trainer, metricks):
		
		"""
		Save metricks
		"""
		
		metricks["scheduler"] = self.scheduler.state_dict()
		metricks["scheduler_name"] = get_class_name(self.scheduler)
		
	
	def load_metricks(self, trainer, metricks):
		
		"""
		Load metricks
		"""
		
		if self.scheduler is not None and metricks is not None and "scheduler" in metricks:
			self.scheduler.load_state_dict(metricks["scheduler"])
	
	
	def on_start_train(self, trainer):
		
		"""
		Start train event
		"""
		
		if self.scheduler is None and trainer.scheduler_enable:
			self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
				trainer.optimizer
			)
	
	
	def on_end_epoch(self, trainer):
		
		"""
		On epoch end
		"""
		
		if self.scheduler is not None:
			loss_val = trainer.train_status.get_loss_val()
			self.scheduler.step(loss_val)
	

class TrainSaveCallback:
	
	
	def detect_type(self, file_name):
	
		import re
		
		file_type = ""
		epoch_index = 0
		
		result = re.match(r'^model-(?P<id>[0-9]+)-optimizer\.data$', file_name)
		if result:
			return "optimizer", int(result.group("id"))
		
		result = re.match(r'^model-(?P<id>[0-9]+)\.data$', file_name)
		if result:
			return "model", int(result.group("id"))
		
		return file_type, epoch_index
	
	
	def save_epoch_indexes(self, model, model_path, epoch_indexes):
		
		"""
		Save epoch by indexes
		"""
		
		model_path = model_path.model_name( model.get_model_name() )
		file_path = model_path.get_model_file_path()
		dir_name = os.path.dirname(file_path)
		files = list_files( dir_name )
		
		for file_name in files:
			
			file_type, epoch_index = self.detect_type(file_name)
			if file_type in ["model", "optimizer"] and not (epoch_index in epoch_indexes):
				
				file_path = os.path.join( dir_name, file_name )
				os.unlink(file_path)
				
	
	
	def get_the_best_epoch(self, model, epoch_count=5, indexes=False):
		
		"""
		Returns teh best epoch
		"""
		
		metrics = model._history.get_metrics(["loss_val", "acc_rel"], with_index=True)
		
		def get_key(item):
			return [item[1], item[2]]

		metrics.sort(key=get_key)
		
		res = []
		res_count = 0
		metrics_len = len(metrics)
		loss_val_last = 100
		for index in range(metrics_len):
			
			res.append( metrics[index] )
			
			if loss_val_last != metrics[index][1]:
				res_count = res_count + 1
			
			loss_val_last = metrics[index][1]
			
			if res_count > epoch_count:
				break
		
		if not indexes:
			return res
			
		res_indexes = []
		for index in range(len(res)):
			res_indexes.append( res[index][0] )
			
		return res_indexes
	
	
	def save_the_best_epoch(self, model, model_path, epoch_count=5):
		
		"""
		Save the best models
		"""
		
		if model._history.epoch_number > 0 and epoch_count > 0:
			
			epoch_indexes = self.get_the_best_epoch(model, epoch_count, indexes=True)
			epoch_indexes.append( model._history.epoch_number )
			
			self.save_epoch_indexes(model, model_path, epoch_indexes)
	
	
	def on_start_train(self, trainer):
		
		"""
		Start train event
		"""
		
		if trainer.model_path is None:
			return
		
		if trainer.load_model:
			save_metrics = trainer.model.load(
				model_path=trainer.model_path,
			)
			
			if save_metrics is not None and "optimizer" in save_metrics:
				trainer.optimizer.load_state_dict(save_metrics["optimizer"])
			
			for callback in trainer.callbacks:
				if hasattr(callback, "load_metricks"):
					callback.load_metricks(trainer, save_metrics)
					
			trainer.train_status.set_model(trainer.model)
			
	
	
	def on_end_epoch(self, trainer):
		
		"""
		On epoch end
		"""
		
		if trainer.model_path is None:
			return
		
		save_metrics = {
			"optimizer": trainer.optimizer.state_dict(),
			"optimizer_name": get_class_name(trainer.optimizer),
		}
		
		for callback in trainer.callbacks:
			if hasattr(callback, "save_metrics"):
				callback.save_metrics(trainer, save_metrics)
		
		model_path = trainer.model_path
		model_path = model_path.file_name( "" )
		model_path = model_path.file_path( "" )
		
		trainer.model.save(
			model_path=model_path,
			save_epoch=trainer.save_epoch,
			save_metrics=save_metrics,
		)
		
		if trainer.save_epoch:
			
			"""
			Save best epoch
			"""
			self.save_the_best_epoch(
				model=trainer.model,
				model_path=trainer.model_path,
				epoch_count=trainer.save_epoch_count
			)
		

class TrainCheckIsTrainedCallback:
	
	def check_is_trained(self, trainer):
		
		"""
		Returns True if model is trained
		"""
		
		epoch_number = trainer.train_status.epoch_number
		acc_train = trainer.train_status.get_acc_train()
		acc_val = trainer.train_status.get_acc_val()
		acc_rel = trainer.train_status.get_acc_rel()
		loss_val = trainer.train_status.get_loss_val()
		
		if epoch_number >= trainer.max_epochs:
			return True
		
		if loss_val < trainer.min_loss_val and epoch_number >= trainer.min_epochs:
			return True
		
		return False
	
	
	def on_end_epoch(self, trainer):
		
		"""
		On epoch end
		"""
		
		is_trained = self.check_is_trained(trainer)
		if is_trained:
			trainer.stop_training()


class Trainer:
	
	def __init__(self, model, *args, **kwargs):
		
		self.model = model
		
		self.train_status = TrainStatus()
		self.train_status.trainer = self
		
		self.train_loader = None
		self.val_loader = None
		self.train_dataset = None
		self.val_dataset = None
		self.batch_size = 64
		
		self.optimizer = None
		self.loss = None
		self.verbose = True
		self.num_workers = os.cpu_count()
		
		self.load_model = kwargs["load_model"] if "load_model" in kwargs else True
		self.model_path = kwargs["model_path"] if "model_path" in kwargs else None
		self.max_epochs = kwargs["max_epochs"] if "max_epochs" in kwargs else 50
		self.min_epochs = kwargs["min_epochs"] if "min_epochs" in kwargs else 3
		self.max_acc_rel = kwargs["max_acc_rel"] if "max_acc_rel" in kwargs else 5
		self.min_loss_val = kwargs["min_loss_val"] if "min_loss_val" in kwargs else -1
		self.batch_size = kwargs["batch_size"] if "batch_size" in kwargs else 64
		
		self.train_dataset = kwargs["train_dataset"] if "train_dataset" in kwargs else False
		self.val_dataset = kwargs["val_dataset"] if "val_dataset" in kwargs else False
		self.tensor_device = kwargs["tensor_device"] if "tensor_device" in kwargs else None
		self.save_epoch = kwargs["save_epoch"] if "save_epoch" in kwargs else True
		self.save_epoch_count = kwargs["save_epoch_count"] if "save_epoch_count" in kwargs else 5
		self.scheduler_enable = kwargs["scheduler_enable"] if "scheduler_enable" in kwargs else True
		
		if "optimizer" in kwargs:
			self.optimizer = kwargs["optimizer"]
		
		if "loss" in kwargs:
			self.loss = kwargs["loss"]
		
		if "num_workers" in kwargs:
			self.num_workers = kwargs["num_workers"]
		
		if "callbacks" in kwargs:
			self.callbacks = kwargs["callbacks"]
		else:
			self.callbacks = [
				TrainCheckIsTrainedCallback(),
				TrainShedulerCallback(),
				TrainAccuracyCallback(),
				TrainVerboseCallback(),
				TrainSaveCallback(),
			]
	
	
	"""	====================== Events ====================== """
	
	def on_start_train(self):
		
		"""
		Start train event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_start_train"):
				callback.on_start_train(self)
		
	
	def on_start_epoch(self):
		
		"""
		Start epoch event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_start_epoch"):
				callback.on_start_epoch(self)
	
	
	def on_start_batch_train(self, batch_x, batch_y):
		
		"""
		Start train batch event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_start_batch_train"):
				callback.on_start_batch_train(self, batch_x, batch_y)
	
	
	def on_end_batch_train(self, batch_x, batch_y, batch_predict, loss):
		
		"""
		End train batch event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_end_batch_train"):
				callback.on_end_batch_train(self, batch_x, batch_y, batch_predict, loss)
	
	
	def on_start_batch_test(self, batch_x, batch_y):
		
		"""
		Start test batch event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_start_batch_test"):
				callback.on_start_batch_test(self, batch_x, batch_y)
	
	
	def on_end_batch_test(self, batch_x, batch_y, batch_predict, loss):
		
		"""
		End test batch event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_end_batch_test"):
				callback.on_end_batch_test(self, batch_x, batch_y, batch_predict, loss)
	
	
	def on_end_epoch(self, **kwargs):
		
		"""
		On epoch end
		"""
		
		self.model._history.add_train_status(self.train_status)
		
		for callback in self.callbacks:
			if hasattr(callback, "on_end_epoch"):
				callback.on_end_epoch(self)
		
	
	def on_end_train(self):
		
		"""
		End train event
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "on_end_train"):
				callback.on_end_train(self)
	
	
	def stop_training(self):
		
		"""
		Stop training
		"""
		
		self.train_status.stop_train()
	
	
	def check_is_trained(self):
		
		"""
		Check is trained
		"""
		
		for callback in self.callbacks:
			if hasattr(callback, "check_is_trained"):
				res = callback.check_is_trained(self)
				if res:
					return True
		
		return False
	
	
	def train(self):
		
		"""
		Train model
		"""
		
		model = self.model
		torch.cuda.empty_cache()
		
		# Get optimizer from mode
		self.optimizer = model.optimizer
		
		# Adam optimizer
		if self.optimizer is None:
			self.optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
		
		# Mean squared error
		if self.loss is None:
			self.loss = torch.nn.MSELoss()
		
		if self.tensor_device is None:
			tensor_device = get_tensor_device()
		
		if self.train_loader is None and self.train_dataset is not None:
			self.train_loader = DataLoader(
				self.train_dataset,
				num_workers=self.num_workers,
				batch_size=self.batch_size,
				drop_last=False,
				shuffle=True
			)
		
		if self.val_loader is None and self.val_dataset is not None:
			self.val_loader = DataLoader(
				self.val_dataset,
				num_workers=self.num_workers,
				batch_size=self.batch_size,
				drop_last=False,
				shuffle=False
			)
		
		module = model.to(tensor_device)
		
		# Do train
		train_status = self.train_status
		train_status.batch_size = self.batch_size
		train_status.do_training = True
		train_status.train_data_count = len(self.train_dataset)
		
		# Start train
		self.on_start_train()
		
		# Train the model
		if self.check_is_trained():
			return
		
		print ("Train model " + str(model.get_model_name()))
		
		try:
		
			while True:
				
				train_status.clear_iter()
				train_status.epoch_number = train_status.epoch_number + 1
				train_status.time_start = time.time()
				self.on_start_epoch()
				
				module.train()
				
				# Train batch
				for batch_x, batch_y in self.train_loader:
					
					batch_x = batch_x.to(tensor_device)
					batch_y = batch_y.to(tensor_device)
					batch_x, batch_y = model.convert_batch(x=batch_x, y=batch_y)
					
					self.on_start_batch_train(batch_x, batch_y)
					
					# Predict
					self.optimizer.zero_grad()
					batch_predict = module(batch_x)
					loss = self.loss(batch_predict, batch_y)
					loss.backward()
					self.optimizer.step()
					
					# Save train status
					train_status.batch_train_iter = train_status.batch_train_iter + 1
					train_status.loss_train_iter = train_status.loss_train_iter + loss.data.item()
					train_status.count_train_iter = train_status.count_train_iter + batch_x.shape[0]
					train_status.time_end = time.time()
					
					self.on_end_batch_train(batch_x, batch_y, batch_predict, loss)
					
					del batch_x, batch_y, batch_predict
					
					# Clear CUDA
					if torch.cuda.is_available():
						torch.cuda.empty_cache()
				
				module.eval()
				
				# val batch
				for batch_x, batch_y in self.val_loader:
					
					batch_x = batch_x.to(tensor_device)
					batch_y = batch_y.to(tensor_device)
					batch_x, batch_y = model.convert_batch(x=batch_x, y=batch_y)
					
					self.on_start_batch_test(batch_x, batch_y)
					
					# Predict
					self.optimizer.zero_grad()
					batch_predict = module(batch_x)
					loss = self.loss(batch_predict, batch_y)
					loss.backward()
					self.optimizer.step()
					
					# Save train status
					train_status.batch_val_iter = train_status.batch_val_iter + 1
					train_status.loss_val_iter = train_status.loss_val_iter + loss.data.item()
					train_status.count_val_iter = train_status.count_val_iter + batch_x.shape[0]
					train_status.time_end = time.time()
					
					self.on_end_batch_test(batch_x, batch_y, batch_predict, loss)
					
					del batch_x, batch_y, batch_predict
					
					# Clear CUDA
					if torch.cuda.is_available():
						torch.cuda.empty_cache()
				
				# Epoch callback
				train_status.time_end = time.time()
				self.on_end_epoch()
				
				if not train_status.do_training:
					break
			
		except KeyboardInterrupt:
			
			print ("")
			print ("Stopped manually")
			print ("")
			
			pass
		
		self.on_end_train()
	

def train(model, *args, **kwargs):
	
	"""
	Start training
	"""
	
	trainer = Trainer(model, *args, **kwargs)
	trainer.train()
		
	return trainer


class FilesListDataset(Dataset):
	
	def __init__(self, files, files_path="", transform=None, get_tensor_from_answer=None):
		
		self.files = files
		self.files_path = files_path
		self.transform = transform
		self.get_tensor_from_answer = get_tensor_from_answer
	
	
	def __getitem__(self, index):
		
		file_path = ""
		answer = torch.tensor([])
		
		if self.get_tensor_from_answer is None:
			file_path = self.files[index]
		else:
			file_path, answer = self.files[index]
		
		if self.files_path != "":
			file_path = os.path.join(self.files_path, file_path)
		
		tensor = self.transform(file_path)
		
		if self.get_tensor_from_answer is not None:
			answer = self.get_tensor_from_answer(answer)
		
		return ( tensor, answer )
	
	def __len__(self):
		return len(self.files)
