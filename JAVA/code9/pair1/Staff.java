package pair1;

import java.time.LocalDate;

public class Staff<T,U> 
{
   private T first;
   private U second;

   public Staff() { first = null; second = null; }
   public Staff(T first, U second) { this.first = first;  this.second = second; }

   public T getFirst() { return first; }
   public U getSecond() { return second; }

   public void setFirst(T newValue) { first = newValue; }
   public void setSecond(U newValue) { second = newValue; }
}

class Main{
	public static void main(String[] args) {
		String name="Tom";
		LocalDate date =LocalDate.of(2018, 1, 1);
		Staff<String,LocalDate> p1 = new Staff<>(name ,date);
		System.out.println("The name is: "+p1.getFirst()+"\nThe date is: "+p1.getSecond());
	}
}
